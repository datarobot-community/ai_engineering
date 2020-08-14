import sys
import json
import requests
import argparse
import csv 
API_KEY, BASE_URL, DEPLOYMENT_ID, DATAROBOT_KEY, PRED_SERVER = '','','','',''
EXPLANATIONS = None
MAX_PREDICTION_FILE_SIZE_BYTES = 52428800  # 50 MB
 
class DataRobotPredictionError(Exception):
    """Raised if there are issues getting predictions from DataRobot"""

def get_pred_server():
    global DATAROBOT_KEY
    headers = {'Content-Type': 'text/plain; charset=UTF-8', 
    'Authorization': 'Token {}'.format(API_KEY)}
 
    url = f"{BASE_URL}/api/v2/predictionServers"
    print(url)

    response = requests.get(
        url,
        headers=headers
    )
    _raise_dataroboterror_for_status(response)
    response_json = response.json()
    for r in response_json['data']:
        if r['url'] == PRED_SERVER:
            DATAROBOT_KEY = r['datarobot-key']
    return

def make_datarobot_deployment_predictions(data,start_date,end_date,cols=None):
    # Set HTTP headers. The charset should match the contents of the file.
    
    get_pred_server()
    headers = {
        'Content-Type': 'text/plain; charset=UTF-8', 
        'Authorization': 'Token {}'.format(API_KEY),
        'Accept':'text/csv'
    }
    if DATAROBOT_KEY:
        headers['datarobot-key'] = DATAROBOT_KEY
    print(DATAROBOT_KEY)
    preds = 'predictions'
    if EXPLANATIONS:
        preds = 'predictionExplanations'

    url = '{pred_server}/predApi/v1.0/deployments/{deployment_id}/{preds}'\
                .format(deployment_id=DEPLOYMENT_ID,pred_server=PRED_SERVER,preds=preds)

    print(url)
    if cols:
        cols_str = "?"
        if cols == 'passthroughColumnsSet':
            cols_str += cols +'=all'
        else:
            cols_l = []
            for c in cols:
                cols_l.append(f"passthroughColumns={c}")
            cols_str += "&".join(cols_l)
        url += cols_str
        if start_date:
            url += f"&predictionsStartDate={start_date}&predictionsEndDate={end_date}"
    elif start_date:
        url += f"?predictionsStartDate={start_date}&predictionsEndDate={end_date}"
    predictions_response = requests.post(
        url,
        data=data,
        headers=headers
    )
    _raise_dataroboterror_for_status(predictions_response)
    return predictions_response.text

def _raise_dataroboterror_for_status(response):
    """Raise DataRobotPredictionError if the request fails along with the response returned"""
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        err_msg = '{code} Error: {msg}'.format(
            code=response.status_code, msg=response.text)
        raise DataRobotPredictionError(err_msg)

def predict(input_file,output_file,**kwargs):
    global API_KEY,DEPLOYMENT_ID,EXPLANATIONS,DATAROBOT_KEY,PRED_SERVER,BASE_URL
    API_KEY = kwargs['API_KEY']
    BASE_URL = kwargs['BASE_URL']
    DEPLOYMENT_ID = kwargs['DEPLOYMENT_ID']
    EXPLANATIONS = kwargs['EXPLANATIONS']
    PRED_SERVER = kwargs['PRED_SERVER']
    cols = None

    # Set passthrough columns
    if 'keep_cols' in kwargs:
        cols = kwargs['keep_cols'].split(',')

    # Include all passthrough columns into result
    if 'passthrough_columns_set' in kwargs:
        cols = 'passthroughColumnsSet'
    
    if 'start_date' in kwargs:
        start_date = kwargs['start_date']
        end_date = kwargs['end_date']
    else:
        start_date, end_date = None, None
    data = open(input_file, 'rb').read()
    data_size = sys.getsizeof(data)
    if data_size >= MAX_PREDICTION_FILE_SIZE_BYTES:
        print(
            'Input file is too large: {} bytes. '
            'Max allowed size is: {} bytes.'
        ).format(data_size, MAX_PREDICTION_FILE_SIZE_BYTES)
        return 1
    try:
        predictions = make_datarobot_deployment_predictions(data, start_date,end_date, cols)
    except DataRobotPredictionError as exc:
        raise(exc)
    except KeyError as exc:
        raise(exc)
    
    # write response to output file
    with open(output_file,'w') as f:
        f.write(predictions)
    return 0

def main():
    return
if __name__ == "__main__":
    sys.exit(main())
