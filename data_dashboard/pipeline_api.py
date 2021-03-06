import json
import logging

import boto3
import botocore
from django.conf import settings

logger = logging.getLogger(__name__)

def s3_resource():
    return boto3.resource(
        's3', aws_access_key_id=settings.AWS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_KEY
    )


def dynamo_client():
    return boto3.client(
        'dynamodb', region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_KEY
    )


def get_files(bucket, path):
    s3resource = s3_resource()
    try:
        obj = s3resource.Object(bucket,
                                "{}/directoryList.json".format(path))
        file_sizes = json.loads(obj.get()['Body'].read())['fileSizes']
        files = list(file_sizes.keys())
        files.sort()
        return files
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            return None
        raise e


def get_report(run_id):
    logger.info("Getting report at {}/{}.json".format(settings.PIPELINE_REPORT_BUCKET, run_id))
    s3resource = s3_resource()
    try:
        obj = s3resource.Object(settings.PIPELINE_REPORT_BUCKET,
                                "{}.json".format(run_id))
        return json.loads(obj.get()['Body'].read())
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            return None
        raise e

def get_run(run_id, branch):
    dbclient = dynamo_client()
    if branch == 'master':
        table = "{}".format(settings.DYNAMO_PIPELINE_TABLE)
    else:
        table = "{}-{}".format(settings.DYNAMO_PIPELINE_TABLE, branch)
    run = dbclient.get_item(TableName=table, Key={'run_id': {'S': run_id}})
    return run['Item']


def list_runs(branch):
    dbclient = dynamo_client()
    if branch == 'master':
        table = "{}".format(settings.DYNAMO_PIPELINE_TABLE)
    else:
        table = "{}-{}".format(settings.DYNAMO_PIPELINE_TABLE, branch)
    lst = dbclient.scan(TableName=table)
    lst['Items'].sort(key=lambda x: x['run_start']['S'], reverse=True)
    return lst['Items']
