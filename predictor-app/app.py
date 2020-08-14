import os
from flask import Flask, flash, request, redirect, url_for, render_template, Response, session, \
    make_response, abort,jsonify,send_from_directory
from werkzeug.utils import secure_filename
from subprocess import check_call
import pandas as pd 
import boto3
from botocore.exceptions import ClientError
import time 
from random import randrange,choices
import requests
from zappa.asynchronous import task, get_async_response
from flask_bootstrap import Bootstrap
import redis
from helper import predict
from pathlib import Path
from flask_session import Session as f_session

class DevConfig:
    FLASK_APP = "app.py"
    SESSION_TYPE = os.environ.get("SESSION_TYPE")
    if SESSION_TYPE and SESSION_TYPE=='redis':
        redis_url = os.environ.get('REDIS_CONN')
        SESSION_REDIS = redis.from_url(redis_url)
    else:
        SESSION_TYPE = 'filesystem'
        SESSION_FILE_DIR = '/tmp/flask_session/'
    PERMANENT_SESSION_LIFETIME = 3600 # 30 minute timeout
    SECRET_KEY = os.environ.get('secret_key')


app = Flask(__name__)
app.config.from_object(DevConfig)
Bootstrap(app)
if os.environ.get('SESSION_TYPE') == 'redis':
    sess = f_session()
    sess.init_app(app)

if os.environ.get('aws_access_key_id'):
    s3_client = boto3.client('s3',
                region_name=os.environ.get('aws_region'),
                aws_access_key_id=os.environ.get('aws_access_key_id'),
                aws_secret_access_key=os.environ.get('aws_secret_access_key'))
else:
    s3_client = boto3.client('s3')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ['csv']

def get_features():
    headers = {'Content-Type': 'text/plain; charset=UTF-8', 
            'Accept':'*/*','Authorization': 'Token {}'.format(session.get('API_KEY'))}
    url = f"{session.get('ENDPOINT_URL')}/api/v2/deployments/{session.get('DEPLOYMENT_ID')}/features"
    try:
        response = requests.get(url,headers=headers)
        features = response.json()['data']
        features = [f['name'] for f in features]
    except ValueError:
        flash('HTTP Response Error: Cannot connect to endpoint.')
        return render_template('score.html')
    except KeyError:
        flash('Session Timeout: Please re-enter your API Key.')
        return redirect(url_for('index'))
    return ",".join(features)

def is_ts(API_KEY,DEPLOYMENT_ID,ENDPOINT_URL):
    # get project id
    headers = {'Content-Type': 'text/plain; charset=UTF-8', 
            'Accept':'*/*','Authorization': 'Token {}'.format(API_KEY)}
    url = f"{ENDPOINT_URL}/api/v2/deployments/{DEPLOYMENT_ID}"
    try:
        response = requests.get(url,headers=headers)
        projectID = response.json()['model']['projectId']
    except KeyError as e:
        raise(e)
    
    url = f"{ENDPOINT_URL}/api/v2/projects/{projectID}"
    try:
        response = requests.get(url,headers=headers)
        is_time_series = response.json()['partition']['useTimeSeries']
    except KeyError as e:
        raise(e)
    return is_time_series

def configure_bucket():
    cors_configuration = {
        'CORSRules': [{
            'AllowedHeaders': ['*'],
            'AllowedMethods': ['GET','PUT'],
            'AllowedOrigins': ['*'],
            'ExposeHeaders': ['ETag'],
            'MaxAgeSeconds': 3000
        }]
    }
    try:
        s3_client.put_bucket_cors(Bucket=session.get('bucket'),CORSConfiguration=cors_configuration)
        print('put bucket cors.')
        signed_url = s3_client.generate_presigned_url(
                    ClientMethod='put_object',
                    Params={
                        'Bucket': session.get('bucket'),
                        'Key': f"uploads/{session.get('filename')}",
                        'ContentType': 'text/csv'
                    },
                    ExpiresIn=3600,
                )
        print(signed_url)
    except ClientError as e:
        raise(e)
    return signed_url

@app.route('/score',methods=['GET','POST'])
def upload_file():
    if request.method == 'POST':
        req_form = request.form
        if (session.get('API_KEY') is None):
            return redirect(url_for('index'))
        if ((session.get('time_series')) == True) and (req_form.get('start_date') == "" or req_form.get('end_date') == ""):
            flash('Start and End Date are required for time series projects.')
            return redirect(url_for('score'))
        
        if req_form['all_cols']=='true':
            cols = "all_columns"
        else:
            cols = ','.join(req_form.getlist('passthrough_columns'))
        
        session['cols'] = cols
        session['save_res'] = bool(req_form.get('save_res'))
        session['explanations'] = req_form.get('explanations')
        session['start_date'] = req_form.get('start_date')
        session['end_date'] = req_form.get('end_date')
        return redirect(url_for('payload',filename=session.get('filename'),bucket=session.get('bucket')))
    elif (session.get('API_KEY') is None):
        return redirect(url_for('index'))

    feats = get_features()
    newfilename = 'input_file_%s.csv'%(randrange(100000, 999999))
    session['filename'] = newfilename

    try:
        signed_url = configure_bucket()
    except Exception as e:
        print(e)
        flash(f"Bucket configuration error: permission denied to {session.get('bucket')}.")
        return redirect(url_for('index'))
    print(signed_url)
    session['time_series'] = is_ts(session.get('API_KEY'),session.get('DEPLOYMENT_ID'),session.get('ENDPOINT_URL'))
    return render_template('score.html',dep_features=feats,
            signed_url=signed_url.split('?')[1],bucket=session.get('bucket'),
            filename=session.get('filename'),
            time_series=session.get('time_series'))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method=='POST':
        if ('API_KEY' in request.form and request.form['API_KEY'] != ''):
            # get list of deployments from api key
            session['API_KEY'] = request.form['API_KEY']
            session['ENDPOINT_URL'] = request.form['ENDPOINT']
            return redirect(url_for('config'))
        else:
            session.clear()
            return render_template('auth.html',api_key='key')
    if os.environ.get('bucket') is None or os.environ.get('bucket') == '':
        flash('S3 bucket not configured.')
        return render_template('auth.html',api_key='key') 
    else:
        session['bucket'] = os.environ.get('bucket')   
    return render_template('auth.html',api_key='key')

@app.route('/config', methods=['GET', 'POST'])
def config():
    if request.method=='POST' and request.form['submit_button'] == 'Save Settings':
        print(request.form)
        if (session['API_KEY'] == ''):
            return redirect(url_for('index'))
        if ('DEPLOYMENT_ID' in request.form): # 
            # get prediction servers from api key and save selected deployment id
            session['DEPLOYMENT_ID'] = request.form['DEPLOYMENT_ID']
            session['PRED_SERVER'] = request.form['PRED_SERVER']
            if 's3_bucket' in request.form:
                session['custom_bucket'] = request.form['s3_bucket']
                session['custom_access_key'] = request.form['access_key']
                session['custom_secret_key'] = request.form['secret_key']
            else:
                session['custom_bucket'],session['custom_access_key'],session['custom_secret_key'] = None,None,None
            return redirect(url_for('upload_file'))
        else:
            # error if no credentials
            flash('Please select a deployment and a prediction server')
            return render_template('config.html')
    elif session.get('API_KEY') != '':
        headers = {'Content-Type': 'text/plain; charset=UTF-8', 
            'Accept':'*/*',
            'Authorization': 'Token {}'.format(session.get('API_KEY'))}
        url = session.get('ENDPOINT_URL')+'/api/v2/deployments'

        try:
            response = requests.get(url,headers=headers)
            deployments = response.json()['data']
            deployments = [d for d in deployments if d['defaultPredictionServer'] is not None]
        except (ValueError, KeyError):
            flash('HTTP Response Error - cannot connect to endpoint.')
            return render_template('config.html')
        
        # get list of pred servers
        headers = {'Content-Type': 'text/plain; charset=UTF-8', 
            'Accept':'*/*','Authorization': 'Token {}'.format(session.get('API_KEY'))}
        url = session.get('ENDPOINT_URL')+'/api/v2/predictionServers/'
        try:
            response = requests.get(url,headers=headers)
            pred_servers = response.json()['data']
        except ValueError:
            flash('HTTP Response Error - cannot connect to endpoint.')
            return render_template('config.html')
        except KeyError:
            flash('Invalid API KEY.')
            return render_template('config.html')
        
        # generate signed url to download past preds
        signed_url = s3_client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': session.get('bucket'),
                'Key': 'saved_preds/%s/%s/preds.csv'%(session.get('API_KEY'),session.get('DEPLOYMENT_ID'))
            }
        )
        return render_template('config.html',deployments=deployments, pred_servers=pred_servers, 
            bucket=session.get('bucket'), filename='preds.csv',
            DEPLOYMENT_ID=session.get("DEPLOYMENT_ID"),API_KEY=session.get("API_KEY"), signed_url=signed_url.split('?')[1])
    return render_template('config.html')

@app.route('/explanations/',methods=['GET','POST'])
def explanations():
    # get and parse explanations from result df
    response = request.get_json()
    key = 'preds/%s_preds.csv'%(session.get('filename').split('.')[0])
    obj = s3_client.get_object(Bucket=session.get('bucket'),Key=key,Range='bytes0-10000000')
    df = pd.read_csv(obj['Body'])

    row_number = int(float(response['row_number']))
    row = df.iloc[row_number,5:]
    feats = [x for x in df.columns if 'FEATURE_NAME' in x]
    strength = [x for x in df.columns if 'QUALITATIVE_STRENGTH' in x]
    val = [x for x in df.columns if 'ACTUAL_VALUE' in x]

    expl_df = pd.concat([row[feats].reset_index().iloc[:,-1],row[strength].reset_index().iloc[:,-1],row[val].reset_index().iloc[:,-1]],axis=1)
    expl_df.columns=['Feature Name','Impact','Value']
    return render_template('preds.html', 
            title="Prediction Explanations",title_val="Explanations",explanations='True',
            column_names=expl_df.columns.values, 
            row_data=list(expl_df.values.tolist()),zip=zip)

@app.route('/preds',methods=['GET', 'POST'])
def preds():
    if (session.get('API_KEY') is None):
        return redirect(url_for('index'))
    elif (session.get('filename') is None):
        return redirect(url_for('upload_file'))
    else:
        # get and display prediction results
        key = 'preds/%s_preds.csv'%(session.get('filename').split('.')[0])
        obj = s3_client.get_object(Bucket=session.get('bucket'),Key=key,Range='bytes0-10000000')

        # generate signed url
        signed_url = s3_client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': session.get('bucket'),
                'Key': key
            }
        )
        print(signed_url)
        # save to custom bucket
        if session.get('custom_bucket'):
            try:
                obj_2 = s3_client.get_object(Bucket=session.get('bucket'),Key=key)
                key='preds/{dep}/preds_{fn}'.format(dep=session.get('DEPLOYMENT_ID'),fn=session.get('filename').split('_')[2])
                client_2=boto3.client('s3',aws_access_key_id=session.get('custom_access_key'),aws_secret_access_key=session.get('custom_secret_key'))
                client_2.put_object(Bucket=session.get('custom_bucket'),Key=key,Body=obj_2['Body'].read())
            except ClientError:
                flash("Could not save to custom bucket %s: Permission Denied."%(session.get('custom_bucket')))
                return redirect(url_for('config'))
        df = pd.read_csv(obj['Body'])
        print(df)
        # display first 100 rows
        if df.shape[0]>100:
            df = df.iloc[0:100]

        print(df.columns)
        if 'EXPLANATION_1_FEATURE_NAME' in df.columns:
            # dont show explanation columns
            cols = [x for x in df.columns if 'EXPLANATION' not in x]
            df=df[cols]
            df.reset_index(inplace=True)
            return render_template('preds.html',
                title="Prediction Results",title_val="Results",hov=True,
                column_names=df.columns.values, signed_url=signed_url.split('?')[1],
                filename=key.split('/')[1], bucket=session.get('bucket'), 
                row_data=list(df.values.tolist()),zip=zip)

        return render_template('preds.html',
            title="Prediction Results",title_val="Results",hov=None,
            column_names=df.columns.values, signed_url=signed_url.split('?')[1],
            filename=key.split('/')[1], bucket=session.get('bucket'), 
            row_data=list(df.values.tolist()),zip=zip)

def get_preds(bucket,key):
    time_end = time.time() + 3*60
    while time.time() < time_end:
        try:
            s3_client.head_object(Bucket=bucket, Key=key)
            return 'done'
        except ClientError:
            time.sleep(5)
            print('waiting for %s'%key)
            continue
    return 'not found'

@app.route('/payload/<filename>/<bucket>/')
def payload(filename,bucket):
    print('in payload function')
    # payload=session['payload']
    payload_vars = '{"bucket":"%s","key":"uploads/%s","DEPLOYMENT_ID":"%s","API_KEY":"%s",\
            "ENDPOINT_URL":"%s","PRED_SERVER":"%s","DATAROBOT_KEY":"%s","explanations": "%s",\
            "cols":"%s","save":"%s","start_date":"%s","end_date":"%s"}'%(session.get('bucket'),session.get('filename'),session.get('DEPLOYMENT_ID'),
                session.get('API_KEY'),session.get('ENDPOINT_URL'),session.get('PRED_SERVER'),
                session.get('DR_KEY'),session.get('explanations'),
                session.get('cols'),session.get('save_res'),session.get('start_date'),session.get('end_date'))
    
    x = longrunner(payload_vars)
    return redirect(url_for('response', response_id=x.response_id,filename=filename))

@app.route('/async-response/<response_id>/<filename>')
def response(response_id,filename):
    response = get_async_response(response_id)
    if response is None:
        flash('Scoring error, please try again')
        return redirect(url_for('upload_file'))

    if response['status'] == 'complete':
        return redirect(url_for('preds',filename=filename))

    time.sleep(5)

    return "Not yet ready. Redirecting.", 302, {
        'Content-Type': 'text/plain; charset=utf-8',
        'Location': url_for('response', response_id=response_id, filename=filename,backoff=5),
        'X-redirect-reason': "Not yet ready.",
    }

@task(capture_response=True)
def longrunner(payload_vars):
    # key = 'preds/%s_preds.csv'%(filename.split('.')[0])
    return predict.handler(payload_vars)

if __name__ == '__main__':
    app.run()