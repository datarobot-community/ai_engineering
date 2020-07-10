import json

import boto3

from .consts import S3_DATA_PARSED_PREFIX, LOGIC_CONNECTOR
from .s3_helpers import s3_get_file_text, gzip_compress, s3_save

S3 = boto3.resource('s3')


def filter_by_logic_connector(event, context):
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    key_path = event['Records'][0]['s3']['object']['key']

    file_text = s3_get_file_text(bucket_name, key_path)

    parsed_lines = parse_by_logic_connector(file_text)

    for logic_connector in parsed_lines:
        save_file(bucket_name,
                  get_s3_key(logic_connector, key_path),
                  parsed_lines[logic_connector])

    msg = f'Successfully converted {key_path}'
    return parsed_lines


def parse_by_logic_connector(text_body):
    parsed_lines = {}
    # parse by LogicConnector
    lines = [line for line in text_body.split('\n') if len(line.strip()) > 0]
    print('len(lines)', len(lines))
    for line in lines:
        json_data = json.loads(line)
        lc = json_data[LOGIC_CONNECTOR]
        parsed_lines[lc] = parsed_lines.get(lc, [])
        parsed_lines[lc].append(line)

    # merge lines
    print(f'parsed_lines keys {len(parsed_lines)}')
    for lc in parsed_lines:
        parsed_lines[lc] = '\n'.join(parsed_lines[lc])

    return parsed_lines


def save_file(bucket_name, key_path, text_body):
    gz_body = gzip_compress(text_body)
    s3_save(bucket_name, key_path, gz_body.getvalue())
    return True


def get_s3_key(logic_connector_id, key_path):
    """Save file with same name, but in LOGIC_CONNECTOR folder"""

    # remove top level folder from s3 key
    file_name = '/'.join(key_path.split('/')[1:]) + '.json.gz'

    s3_key = f'{S3_DATA_PARSED_PREFIX}/{LOGIC_CONNECTOR}_{logic_connector_id}/' + file_name
    return s3_key
