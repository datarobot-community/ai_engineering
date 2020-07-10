###
#
# Lambda to call DataRobot Prediction API request.
# This Lambda is simply acting as a proxy via API Gateway to pass an API gateway call through to DataRobot
#
# Expects and returns data in format outlined by Snowflake for External Functions
# Returns score towards positive class label 1 for passenger survival
# Kaggle titanic set binary classifier
#
# Mike Taveirne (doyouevendata) 6/20/2020
#
###

import os
import json
#from pandas.io.json import json_normalize
import requests
import pandas as pd
import csv

def lambda_handler(event, context):

    # set default status to OK, no DR API error
    status_code = 200
    dr_error = ""

    # The return value will contain an array of arrays (one inner array per input row).
    array_of_rows_to_return = [ ]

    try:
        # obtain secure environment variables to reach out to DataRobot API
        DR_DPE_HOST = os.environ['dr_dpe_host']
        DR_USER = os.environ['dr_user']
        DR_TOKEN = os.environ['dr_token']
        DR_DEPLOYMENT = os.environ['dr_deployment']
        DR_KEY = os.environ['dr_key']
        
        # retrieve body containing input rows
        event_body = event["body"]

        # retrieve payload from body
        payload = json.loads(event_body)

        # retrieve row data from payload
        payload_data = payload["data"]

        # map list of lists to expected inputs
        cols = ['row', 'NAME', 'SEX', 'PCLASS', 'FARE', 'CABIN', 'SIBSP', 'EMBARKED', 'PARCH', 'AGE']
        df = pd.DataFrame(payload_data, columns=cols)
        
        print("record count is: " + str(len(df.index)))
        
        # assemble and send scoring request
        headers = {'Content-Type': 'text/csv; charset=UTF-8', 'Accept': 'text/csv', 'datarobot-key': DR_KEY}
        response = requests.post(DR_DPE_HOST + '/predApi/v1.0/deployments/%s/predictions' % (DR_DEPLOYMENT),
            auth=(DR_USER, DR_TOKEN), data=df.to_csv(), headers=headers)
        
        # bail if anything other than a successful response occurred
        if response.status_code != 200:
            dr_error = str(response.status_code) + " - " + str(response.content)
            print("dr_error: " + dr_error)
            raise
        
        array_of_rows_to_return = []
        
        row = 0
        wrapper = csv.reader(response.text.strip().split('\n'))
        header = next(wrapper)
        idx = header.index('SURVIVED_1_PREDICTION')
        for record in wrapper:
            array_of_rows_to_return.append([row, record[idx]])
            row += 1
        
        # send data back in required snowflake format
        json_compatible_string_to_return = json.dumps({"data" : array_of_rows_to_return})

    except Exception as err:
        # 400 implies some type of error.
        status_code = 400
        # Tell caller what this function could not handle.
        json_compatible_string_to_return = 'failed'
        
        # if the API call failed, update the error message with what happened
        if len(dr_error) > 0:
            print("error")
            json_compatible_string_to_return = 'failed; DataRobot API call request error: ' + dr_error

    # Return the return value and HTTP status code.
    return {
        'statusCode': status_code,
        'body': json_compatible_string_to_return
    }
