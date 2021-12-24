import json
import logging

import boto3

from chalicelib import events

_logger = logging.getLogger()


def publish(queue_url: str, event: events.SQSEvent):
    _logger.info("Publishing SQS event", extra={"queue_url": queue_url, "event": event})
    client = boto3.client('sqs')
    client.send_message(QueueUrl=queue_url, MessageBody=json.dumps(event))


def iterate_messages(queue_url: str):
    sqs = boto3.resource('sqs')
    queue = sqs.Queue(QueueUrl=queue_url)
    messages = queue.receive_messages()
    while messages:
        for message in messages:
            message.delete()
            yield json.loads(message.body)
        messages = queue.receive_messages()


def extract_sns_to_sqs_message(message):
    raw_data = message.get("Message")
    return json.loads(raw_data) if raw_data else None
