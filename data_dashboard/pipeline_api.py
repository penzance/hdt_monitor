import boto3
import json
from django.conf import settings


def s3_resource():
    return boto3.resource('s3')


def dynamo_client():
    return boto3.client('dynamodb', region_name=settings.AWS_REGION)


def get_report(pipeline_id):
    s3resource = s3_resource()
    obj = s3resource.Object(settings.PIPELINE_REPORT_BUCKET,
                            "{}.json".format(pipeline_id))
    return json.loads(obj.get()["Body"].read())


def get_pipeline(pipeline_id):
    dbclient = dynamo_client()
    pipeline = dbclient.get_item(TableName=settings.DYNAMO_PIPELINE_TABLE,
                                 Key={'pipeline_id': {'S': pipeline_id}})
    return pipeline['Item']


def list_pipelines():
    dbclient = dynamo_client()
    lst = dbclient.scan(TableName=settings.DYNAMO_PIPELINE_TABLE)
    lst['Items'].sort(key=lambda x: x['pipeline_created']['S'], reverse=True)
    return lst['Items']
