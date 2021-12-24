import json
import logging

import boto3


_logger = logging.getLogger()


def publish(topic: str, event):
    _logger.info("Publishing event", extra={"topic": topic, "event": event})
    client = boto3.client('sns')
    client.publish(TopicArn=topic, Message=json.dumps(event))