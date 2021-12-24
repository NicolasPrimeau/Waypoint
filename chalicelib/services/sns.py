import json

import boto3


def publish(topic: str, event):
    client = boto3.client('sns')
    client.publish(TopicArn=topic, Message=json.dumps(event))
