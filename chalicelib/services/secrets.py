import boto3


def get_secrets(secret_name: str, region_name: str) -> str:
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    return client.get_secret_value(
        SecretId=secret_name
    )['SecretString']
