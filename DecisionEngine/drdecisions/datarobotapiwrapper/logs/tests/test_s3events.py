import boto3
from django.test import TestCase
from moto import mock_s3

from price.logs.s3_helpers import s3_create_bucket
from ..s3events import save_file, get_s3_key, s3_get_file_text, \
    parse_by_logic_connector, filter_by_logic_connector

BUCKET_NAME = 'bucket-unit-test'


class S3LogTestCase(TestCase):

    def setUp(self):
        self.s3 = boto3.client('s3')
        self.key_path = 'path/file'
        self.text_body = '''line1\nline2\n'''
        self.lines_cnt = len(self.text_body.split('\n'))

    def test_parse_by_logic_connector(self):
        json_lines = ['{"age": 111, "str_field": "str_value1", "logic_connector": 1}',
                      '{"age": 222, "str_field": "str_value2", "logic_connector": 2}',
                      '{"age": 333, "str_field": "str_value3", "logic_connector": 3}',
                      '{"age": 22,  "str_field": "str_value22", "logic_connector": 2}']
        parsed_lines = parse_by_logic_connector('\n'.join(json_lines))

        assert len(parsed_lines) == 3
        assert parsed_lines[2] == '\n'.join([json_lines[1], json_lines[3]])

    @mock_s3
    def test_filter_by_logic_connector(self):
        s3_create_bucket(BUCKET_NAME)
        json_lines = ['{"age": 111, "str_field": "str_value1", "logic_connector": 1}',
                      '{"age": 222, "str_field": "str_value2", "logic_connector": 2}',
                      '{"age": 333, "str_field": "str_value3", "logic_connector": 3}',
                      '{"age": 22,  "str_field": "str_value22", "logic_connector": 2}']
        text_body = '\n'.join(json_lines)
        file_name = 'test_filet.txt'
        key_path = 'path/' + file_name
        save_file(BUCKET_NAME, key_path, text_body)

        s3_dict = {'s3': {'bucket': {'name': BUCKET_NAME},
                          'object': {'key': key_path}}}

        event = {'Records': [s3_dict, ]}
        context = {}

        parsed_lines = filter_by_logic_connector(event, context)

        assert len(parsed_lines) == 3
        logic_connector_id = 1
        assert len(parsed_lines[logic_connector_id].split('\n')) == 1
        logic_connector_id = 2
        assert len(parsed_lines[logic_connector_id].split('\n')) == 2
        logic_connector_id = 3
        assert len(parsed_lines[logic_connector_id].split('\n')) == 1

    @mock_s3
    def test_get_file_text(self):
        s3_create_bucket(BUCKET_NAME)

        saved_len = save_file(BUCKET_NAME, self.key_path, self.text_body)

        text = s3_get_file_text(BUCKET_NAME, self.key_path)

        assert text == self.text_body

    @mock_s3
    def test_save_file(self):
        s3_create_bucket(BUCKET_NAME)

        save_file(BUCKET_NAME, self.key_path, self.text_body)
        text_body = s3_get_file_text(BUCKET_NAME, self.key_path)
        # check that file saved to s3
        assert text_body == self.text_body

    def test_get_s3_key(self):
        file_name = 'file2'
        key_path = 'path/' + file_name
        logic_connector_id = 123

        key = get_s3_key(logic_connector_id, key_path)

        assert str(logic_connector_id) in key
        assert file_name in key
