from time import sleep

#import boto3
from django.conf import settings

#from datarobotapiwrapper.logs.s3_helpers import s3_signed_url
from datarobotapiwrapper.models import LogFile

#athena = boto3.client('athena')


class LogController:

    @staticmethod
    def update_log(logic_connector_id):
        database = settings.GLUE_DATABASE
        table = f'logic_connector_{logic_connector_id}'
        query = f'SELECT * FROM "{database}"."{table}";'
        print('query', query)
        logs_path = 'logs/'
        s3_bucket = settings.S3_DATA_BUCKET
        s3_ouput = f's3://{s3_bucket}/{logs_path}'

        # aws api gateway timeout = 30sec, let's wait up to 25
        wait_seconds = 25
        query_id = LogController.run_query(query, database, s3_ouput)
        s3_key = logs_path + query_id + '.csv'
        LogFile(logic_connector_id=logic_connector_id,
                s3_bucket=s3_bucket,
                s3_key=s3_key).save()
        LogController.query_waiter(query_id, wait_seconds=wait_seconds)

        return settings.S3_DATA_BUCKET, s3_key

    @staticmethod
    def run_query(query, database, s3_output):
        ''' context = {'Database': database}
        configuration = {'OutputLocation': s3_output}

        response = athena.start_query_execution(
            QueryString=query,
            QueryExecutionContext=context,
            ResultConfiguration=configuration)

        query_execution_id = response['QueryExecutionId']
        print('Execution ID: ' + query_execution_id) '''

        return query_execution_id

    @staticmethod
    def query_waiter(query_execution_id, wait_seconds):
        ''' # wait for
        while wait_seconds > 0:
            print('wait_seconds', wait_seconds)
            sleep(1)
            wait_seconds -= 1
            response = athena.get_query_execution(
                QueryExecutionId=query_execution_id)
            state = response['QueryExecution']['Status']['State']
            if state not in ['QUEUED', 'RUNNING']:
                print('get_query_execution', response)
                return True
        print('get_query_execution', response) '''
        return False

    @staticmethod
    def generate_report_url(log_file):
        return ''
        #return s3_signed_url(log_file.s3_bucket, log_file.s3_key)
