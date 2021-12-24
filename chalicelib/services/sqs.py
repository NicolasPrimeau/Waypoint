import json
import logging

import boto3


_logger = logging.getLogger()


class SQSEvent(dict):
    pass


def publish(queue_url: str, event: SQSEvent):
    _logger.info("Publishing SQS event", extra={"queue_url": queue_url, "event": event})
    client = boto3.client('sqs')
    client.send_message(QueueUrl=queue_url, MessageBody=json.dumps(event))
