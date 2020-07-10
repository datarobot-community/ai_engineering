from unittest.mock import patch

import boto3
from django.test import TestCase
from pytest import mark

from price.logs.controllers import LogController, athena
from price.models import LogFile

QUERY_ID = 'query_id_1234'
ATHENA_SUCCEEDED = {'QueryExecutionId': 'guid-1', 'QueryExecution': {'Status': {'State': 'SUCCEEDED'}}}
ATHENA_RUNNING = {'QueryExecutionId': 'guid-1', 'QueryExecution': {'Status': {'State': 'RUNNING'}}}
ATHENA_QUEUED = {'QueryExecutionId': 'guid-1', 'QueryExecution': {'Status': {'State': 'QUEUED'}}}
ATHENA_RESPONSES = [
    ATHENA_QUEUED,
    ATHENA_RUNNING,
    ATHENA_SUCCEEDED,
]


class TestLogController(TestCase):

    def setUp(self):
        self.s3 = boto3.client('s3')
        self.bucket = 'bucket-unit-test'
        self.key_path = 'path/file'
        self.text_body = '''line1\nline2\n'''
        self.lines_cnt = len(self.text_body.split('\n'))

    @patch.object(LogController, 'run_query', return_value=QUERY_ID)
    @patch.object(LogController, 'query_waiter', return_value=True)
    @patch('price.logs.controllers.athena')
    @mark.django_db
    def test_update_log(self, mock_athena, mock_query_waiter, mock_run_query):
        logic_connector_id = 1111
        bucket, key = LogController.update_log(logic_connector_id)
        mock_run_query.assert_called_once()
        mock_query_waiter.assert_called_once_with(
            QUERY_ID,
            wait_seconds=25)
        lf = LogFile.objects.filter(logic_connector_id=logic_connector_id)[0]
        assert lf.s3_key == f'logs/{QUERY_ID}.csv'

    @patch.object(athena, 'start_query_execution', return_value=ATHENA_SUCCEEDED)
    def test_run_query(self, mock_start_query_execution):
        query = 'select * from no_table'
        DB = 'no_db'
        s3_output = 's3_output'
        response = LogController.run_query(query, DB, s3_output)
        assert response == ATHENA_SUCCEEDED['QueryExecutionId']
        mock_start_query_execution.assert_called_once_with(
            QueryExecutionContext={'Database': DB}, QueryString=query,
            ResultConfiguration={'OutputLocation': s3_output}
        )

    @patch.object(athena, 'get_query_execution')
    def test_query_waiter(self, mock_get_query_execution):
        mock_get_query_execution.side_effect = ATHENA_RESPONSES
        response = LogController.query_waiter(
            ATHENA_QUEUED['QueryExecutionId'],
            wait_seconds=22)
        self.assertEqual(mock_get_query_execution.call_count, len(ATHENA_RESPONSES))
        self.assertTrue(response)

    @patch.object(athena, 'get_query_execution')
    def test_query_waiter_false(self, mock_get_query_execution):
        mock_get_query_execution.side_effect = ATHENA_RESPONSES
        response = LogController.query_waiter(
            ATHENA_QUEUED['QueryExecutionId'],
            wait_seconds=2)
        self.assertEqual(mock_get_query_execution.call_count, len(ATHENA_RESPONSES) - 1)
        self.assertFalse(response)
