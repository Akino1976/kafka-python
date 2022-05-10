import json
import logging
import operator
import os
from collections.abc import Generator
from typing import Any, Optional

import boto3
import botocore
import configparser

import settings

logger = logging.getLogger(__name__)
logging.getLogger("boto3").setLevel(logging.CRITICAL)
logging.getLogger("botocore").setLevel(logging.CRITICAL)


def _get_proxy(service_name: str) -> Optional[str]:
    if (service_proxy := os.getenv("MOCK_AWS_HOST")):
        return service_proxy

    return os.getenv("MOCK_AWS_HOST")


def get_client(service_name: str) -> boto3.session.Session.client:
    if operator.contains(settings.ENVIRONMENT, "prod"):
        logger.error("Dont use helper code in production... exit")
        return None

    proxy = _get_proxy(service_name)

    params = dict(
        service_name=service_name,
        region_name="eu-west-1",
        config=botocore.config.Config(connect_timeout=1, read_timeout=10, retries={"max_attempts": 5}),
    )

    if proxy is not None:
        params["use_ssl"] = proxy.startswith("https://")
        params["config"].proxies = {"http": proxy}

    return boto3.client(**params)


def empty_bucket(bucket: str):
    client = get_client(service_name="s3")
    paginator = client.get_paginator("list_objects_v2")
    keys = []
    for page in paginator.paginate(Bucket=bucket, MaxKeys=1000):
        if 'Contents' in page:
            keys += [item['Key'] for item in page['Contents']]
    if len(keys) > 0:
        client.delete_objects(Bucket=bucket, Delete={"Objects": [{"Key": key} for key in keys]})


def get_object(bucket_name: str, key: str) -> bytes:
    client = get_client(service_name="s3")
    try:
        response = client.get_object(Bucket=bucket_name, Key=key)
    except Exception as error:
        return error
    return response["Body"].read()


def bucket_exists(client, bucket_name: str) -> bool:
    try:
        client.head_bucket(Bucket=bucket_name)

        return True
    except botocore.exceptions.ClientError:
        return False


def purge_queue(queue_name: str):
    client = get_client(service_name="sqs")
    sqs_queue_body = client.get_queue_url(QueueName=queue_name)
    try:
        client.purge_queue(QueueUrl=sqs_queue_body.get("QueueUrl"))
    except Exception:
        return None


def list_object_names(bucket_name: str) -> list[str]:
    bucket_objects = []
    client = get_client(service_name="s3")
    paginator = client.get_paginator('list_objects')
    for page in paginator.paginate(Bucket=bucket_name):
        bucket_objects += [s3_object.get("Key") for s3_object in page.get("Contents", [])]
    return bucket_objects
