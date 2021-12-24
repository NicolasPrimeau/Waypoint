from typing import Optional

import boto3
import botocore.exceptions


def get_file_data(s3_bucket: str, s3_key: str) -> Optional:
    s3 = boto3.resource('s3')
    try:
        return s3.Bucket(s3_bucket).Object(s3_key).get()['Body'].read().decode("utf-8")
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            return None
        raise e


def put_file_data(s3_bucket: str, s3_key: str, data):
    s3 = boto3.resource('s3')
    s3.Bucket(s3_bucket).Object(s3_key).put(Body=data.encode("utf-8"))
