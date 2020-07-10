import boto3
from django.conf import settings

from .consts import S3_DATA_PARSED_PREFIX

s3 = boto3.client('s3')
glue = boto3.client('glue')


def update_crawler(event, context):
    """Add logic_connector_* folders to Glue Crawler, that will update/create DataCatalog tables """

    response = s3.list_objects_v2(
        Bucket=settings.S3_DATA_BUCKET,
        Delimiter='/',
        Prefix=S3_DATA_PARSED_PREFIX + '/',
    )

    if ('CommonPrefixes' not in response) or len(response['CommonPrefixes']) < 1:
        print(f'No folders in {settings.S3_DATA_BUCKET}')
        return None

    s3targets = []
    for s3target in response['CommonPrefixes']:
        s3targets.append(
            {'Path': f's3://{settings.S3_DATA_BUCKET}/{s3target["Prefix"]}', 'Exclusions': []}
        )

    crawler = glue.get_crawler(Name=settings.DATA_CRAWLER)

    if crawler['Crawler']['Targets']['S3Targets'] == s3targets:
        print('S3Targets not changed')
    else:
        print('Old s3targets', crawler['Crawler']['Targets']['S3Targets'])
        response = glue.update_crawler(
            Name=settings.DATA_CRAWLER,
            Targets={'S3Targets': s3targets})
        print('New s3targets', s3targets)

    response = glue.start_crawler(Name=settings.DATA_CRAWLER)
    print(f'{settings.DATA_CRAWLER} started. {response}')
