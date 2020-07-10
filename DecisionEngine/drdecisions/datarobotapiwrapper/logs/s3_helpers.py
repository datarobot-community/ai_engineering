import gzip
from io import BytesIO

import boto3

S3 = boto3.resource('s3')
s3_client = boto3.client('s3')


def s3_get_file_text(bucket_name, key_path, gzip=True):
    s3_object = S3.Object(bucket_name, key_path)
    response = s3_object.get()
    if gzip:
        text_body = gzip_uncompress(response)
    else:
        text_body = response['Body'].read().decode('utf-8')
    return text_body


def s3_save(bucket_name, key_path, file_body, gzip=True):
    s3_object_parsed = S3.Object(bucket_name, key_path)
    kwargs = {
        'ContentType': 'application/json',
        'Body': file_body}
    if gzip:
        kwargs['ContentEncoding'] = 'gzip'
    s3_object_parsed.put(**kwargs)


def s3_signed_url(bucket, key):
    # Generate the URL to get 'key-name' from 'bucket-name'
    params = {'Bucket': bucket,
              'Key': key}
    url = s3_client.generate_presigned_url(
        ClientMethod='get_object',
        Params=params)
    return url


def gzip_uncompress(response):
    bytestream = BytesIO(response['Body'].read())
    text_body = gzip.GzipFile(mode='rb', fileobj=bytestream).read().decode('utf-8')
    return text_body


def gzip_compress(text_body):
    gz_body = BytesIO()
    with gzip.GzipFile(fileobj=gz_body, mode='wb', compresslevel=9) as gz:
        gz.write(text_body.encode('utf-8'))  # convert unicode strings to bytes
    # GzipFile has written the compressed bytes into our gz_body
    return gz_body


def s3_key_existing_size(bucket, key):
    """return the key's size if it exist, else None"""
    response = s3_client.list_objects_v2(
        Bucket=bucket,
        Prefix=key)

    for obj in response.get('Contents', []):
        if obj['Key'] == key:
            return obj['Size']


def s3_create_bucket(bucket, region='us-east-2'):
    print('*****', region)
    if region == 'us-east-1':
        response = S3.create_bucket(
            Bucket=bucket)
    else:
        CreateBucketConfiguration = {'LocationConstraint': region}
        response = S3.create_bucket(
            Bucket=bucket,
            CreateBucketConfiguration=CreateBucketConfiguration)

    return response
