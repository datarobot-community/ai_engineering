import boto3

from django.conf import settings

#firehose_client = boto3.client('firehose')


def put_record(data_list):
    """AWS Firehorse recommends newline (\n) or some other character
    unique within the data delimeter for records"""

    records = [{'Data': record + '\n'} for record in data_list]
    # max size for 1 record - 1000kb, so better to split rows
    """  response = firehose_client.put_record_batch(
        DeliveryStreamName=settings.DELIVERY_STREAM,
        Records=records) """
    response =  ""
    # print('response', response)
