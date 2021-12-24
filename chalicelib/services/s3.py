import logging
from typing import Optional

import boto3
import botocore.exceptions


_logger = logging.getLogger()


def get_file_data(s3_bucket: str, s3_key: str) -> Optional:
    s3 = boto3.resource('s3')
    try:
        _logger.info(f"Fetching s3://{s3_bucket}/{s3_key}")
        return s3.Bucket(s3_bucket).Object(s3_key).get()['Body'].read().decode("utf-8")
    except botocore.exceptions.ClientError as e:
        _logger.info(e.response)
        if e.response['Error']['Code'] == 'NoSuchKey':
            _logger.info(f"s3://{s3_bucket}/{s3_key} does not exist")
            return None
        else:
            raise e


def put_file_data(s3_bucket: str, s3_key: str, data):
    s3 = boto3.resource('s3')
    s3.Bucket(s3_bucket).Object(s3_key).put(Body=data.encode("utf-8"))
