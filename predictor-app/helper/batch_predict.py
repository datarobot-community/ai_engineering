import argparse
import contextlib
import json
import logging
import os
import sys
import time
import threading
import requests
import ast
try:
    from urllib2 import urlopen, HTTPError, Request
except ImportError:
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError

API_KEY,ENDPOINT,DEPLOYMENT_ID = '','',''
POLL_INTERVAL = 15
CHUNK = 64 * 1024

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)
 
capath = None

class DataRobotPredictionError(Exception):
    """Raised if there are issues getting predictions from DataRobot"""
 
 
class JobStatus(object):
    INITIALIZING = 'INITIALIZING'
    RUNNING = 'RUNNING'
    COMPLETED = 'COMPLETED'
    ABORTED = 'ABORTED'
 
    DOWNLOADABLE = [RUNNING, COMPLETED, ABORTED]

def post_req(url,headers,data):
    response = requests.post(
        url=url,
        headers=headers,
        data=data
    )
    resp = response.json()
    print(resp)
    credentialId = resp['credentialId']
    return credentialId

def patch_req(url,headers,data):
    response = requests.patch(
        url=url,
        headers=headers,
        data=data
    )
    resp = response.json()
    print(resp)
    credentialId = resp['credentialId']
    return credentialId

def get_cred_id(name,url,headers):
    response = requests.get(
        url=url,
        headers=headers
    )
    resp = response.json()
    creds = [x['credentialId'] for x in resp['data'] if x['name']==name]
    return "".join(creds)

def create_credentials():
    # get bucket credentials
    aws_access_key_id = os.environ.get('aws_access_key_id')
    aws_secret_access_key = os.environ.get('aws_secret_access_key')
    session_token = ""
    if 'aws_session_token' in os.environ:
        session_token = ', "awsSessionToken":"%s"'%(os.environ.get('aws_session_token'))

    # create credentials in DR
    cred_name = 'predictor-s3-creds'
    url = f"{ENDPOINT}/api/v2/credentials/"
    data = '{"name":"%s",\
            "credentialType":"s3",\
            "awsAccessKeyId": "%s", \
            "awsSecretAccessKey": "%s"%s}'%(cred_name,aws_access_key_id,aws_secret_access_key,session_token)
    headers = {'Authorization': 'Token {}'.format(API_KEY),
                'Content-Type': 'application/json'}
    try:
        credentialId = post_req(url,headers,data)
    except Exception as e: # credentials already exist
        credentialId = get_cred_id(cred_name,url,headers)
        d = ast.literal_eval(data)
        d.pop('credentialType',None)
        patch_req(url+credentialId,headers,str(d))
        print(credentialId)
    return credentialId

def batch_preds_s3(payload):
    session = requests.Session()
    session.headers = {
        'Authorization': 'Bearer {}'.format(API_KEY)
    }
    url = f"{ENDPOINT}/api/v2/batchPredictions/"
    print(url)
    # Send the job
    resp = session.post(url, json=payload)
    print(resp.text)
    resp.raise_for_status()

    job = resp.json()
    print(job)

    while job['status'] not in {'COMPLETED', 'ABORTED'}:
        time.sleep(5)
        resp = session.get(job['links']['self'])
        resp.raise_for_status()

        job = resp.json()
    print('job finished with status: {}'.format(job['status']))
    return job['status']
 
def predict(input_file,output_file,**kwargs):
    global API_KEY,ENDPOINT,DEPLOYMENT_ID
    s3 = True
    API_KEY = kwargs['API_KEY']
    ENDPOINT = kwargs['BASE_URL']
    DEPLOYMENT_ID = kwargs['DEPLOYMENT_ID']
    EXPLANATIONS = kwargs['EXPLANATIONS']
    
    payload = {
        'deploymentId': DEPLOYMENT_ID
    }

    # Set max prediction explanations
    if EXPLANATIONS == True:
        payload['maxExplanations'] = 3

    # Set passthrough columns
    if 'keep_cols' in kwargs:
        payload['passthroughColumns'] = kwargs['keep_cols'].split(',')
    if 'start_date' in kwargs:
        payload['predictionsStartDate'] = kwargs['start_date']
        payload['predictionsEndDate'] = kwargs['end_date']

    # Include all passthrough columns into result
    if 'passthrough_columns_set' in kwargs:
        payload['passthroughColumnsSet'] = 'all'
    if s3:
        print('getting credentials...')
        credential_id = create_credentials()
        print(f"creds: {credential_id}")
        payload['intakeSettings'] = {'type':'s3', 
                                    'url':input_file, 
                                    'credentialId':credential_id}
        payload['outputSettings'] = {'type':'s3',
                                    'url':output_file,
                                    'credentialId':credential_id}
        print(payload)
        try:
            batch_preds_s3(payload)
            # make_datarobot_batch_predictions(input_file, output_file, payload)
        except DataRobotPredictionError as err:
            logger.exception('Error: {}'.format(err))
            return 1
 
    return 0

if __name__ == '__main__':
    sys.exit(main())
 