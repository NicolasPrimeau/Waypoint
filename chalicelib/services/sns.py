import json
import logging

import boto3

from chalicelib import events

_logger = logging.getLogger()


def publish(topic: str, event: events.SNSEvent):
    _logger.info("Publishing SNS event", extra={"topic": topic, "event": event})
    client = boto3.client('sns')
    client.publish(TopicArn=topic, Message=json.dumps(event))


def publish_pretty(topic: str, event: events.SNSEvent):
    _logger.info("Pretty publishing SNS event", extra={"topic": topic, "event": event})
    client = boto3.client('sns')
    client.publish(TopicArn=topic, Message=json.dumps(event, indent=4, sort_keys=True))
