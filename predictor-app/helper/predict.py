import json
import urllib.parse
import boto3
from subprocess import check_call
import csv
from datetime import datetime
import sys
import ast
from botocore.exceptions import ClientError
from flask import url_for
from helper import single_predict,batch_predict
import time
import os

if os.environ.get('aws_access_key_id'):
    s3 = boto3.client('s3',
        region_name='us-east-2',
        aws_access_key_id=os.environ.get('aws_access_key_id'),
        aws_secret_access_key=os.environ.get('aws_secret_access_key'))
    print('here')
else:
    s3 = boto3.client('s3')
    print(os.environ)
MAX_PREDICTION_FILE_SIZE_BYTES = 10485760

def batch_needed(filename):
    data = open(filename, 'rb').read()
    data_size = sys.getsizeof(data)
    print(data_size)
    if data_size >= MAX_PREDICTION_FILE_SIZE_BYTES:
        return True
    return False

def append_csvs(in_file,out_file):
    fout=open(out_file,"a")   
    f = open(in_file,"r")
    f.readline() # skip the header
    for line in f:
         fout.write(line)
    f.close()
    fout.close()
    return out_file

def wait_for_file(bucket,key):
    # wait 15 minutes for file
    time_end = time.time() + 15*60
    while time.time() < time_end:
        try:
            obj = s3.head_object(Bucket = bucket, Key = key)
            size = obj['ContentLength']
            return size
        except ClientError as e:
            if e.response['Error']['Code']=='403':
                return e
            elif e.response['Error']['Code']=='404':
                print('not found - retrying...')
                time.sleep(5)
                continue
            else:
                return e
    return 'File not found'

def handler(event):
    # prepare config vars for predict function
    event = ast.literal_eval(event)
    bucket = event['bucket']
    key = event['key']
    new_key = 'preds/%s_preds.csv'%(key.split('/')[1].split('.')[0])
    input_file = '/tmp/'+ key.split('/')[1]
    output_csv = '/tmp/%s_preds.csv'%(key.split('/')[1].split('.')[0])
    
    auth_args = {'API_KEY': event['API_KEY'],
                'DEPLOYMENT_ID': event['DEPLOYMENT_ID'],
                'BASE_URL' : event['ENDPOINT_URL'],
                'EXPLANATIONS': (event['explanations'] == 'explanations')}

    cols = event['cols']
    if cols == 'all_columns':
        auth_args['passthrough_columns_set'] = True
    elif cols:
        auth_args['keep_cols'] = cols
    if event['start_date'] != "None":
        auth_args['start_date'] = event['start_date']
        auth_args['end_date'] = event['end_date']
    print(auth_args)

    # wait until file present 
    file_info = wait_for_file(bucket,key)
    if isinstance(file_info,str):
        return file_info
    elif not isinstance(file_info,int):
        return file_info
    # run predict function
    if file_info >= MAX_PREDICTION_FILE_SIZE_BYTES:
        print('batch predict')
        try:
            batch_predict.predict(input_file=f"s3://{bucket}/{key}", output_file=f"s3://{bucket}/{new_key}", **auth_args)
        except Exception as e:
            return
    else:
        s3.download_file(bucket,key,input_file)
        auth_args['PRED_SERVER'] = event['PRED_SERVER']
        try:
            single_predict.predict(input_file=input_file, output_file=output_csv, **auth_args)
            s3.upload_file(output_csv, bucket, new_key) # upload result file for consumption in app
        except Exception as e:
            return
        # save predictions to audit
        if event['save'] == 'True':
            save_key = 'saved_preds/%s/%s/preds.csv'%(event['API_KEY'],event['DEPLOYMENT_ID'])
            saved_file = '/tmp/saved.csv'
            try:
                s3.download_file(bucket, save_key, saved_file)
                output_csv=append_csvs(in_file=output_csv,out_file=saved_file)
            except ClientError as e:
                print("file doesn't exist yet")
            print('saving file to %s'%(saved_file))
            s3.upload_file(output_csv, bucket, save_key)
    
    s3.delete_object(Bucket=bucket,Key=key) # delete uploaded file 


