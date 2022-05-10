import json
import logging
import os
from typing import Any

import boto3
import botocore
from botocore.exceptions import ClientError

import common.connection as connection
import settings

logger = logging.getLogger(__name__)

CONTENT_TYPE_ND_JSON = 'application/x-ndjson'
ND_JSON_FILE_SUFFIX = '.ndjson'

ORIGIN_BUCKET_NAME_META_KEY = 'origin-bucket-name'
ORIGIN_OBJECT_KEY_META_KEY = 'origin-object-key'
APP_VERSION_META_KEY = 'app-version'


def _format_newline_delimited_json(records: list[dict[str, Any]]) -> str:
    return "\n".join([json.dumps(record, ensure_ascii=False) for record in records if record])


def get_object(bucket: str, key: str) -> botocore.response.StreamingBody:
    client = connection.get_client(service_name="s3")
    try:
        s3_object = client.get_object(
            Bucket=bucket,
            Key=key,
        )
        return s3_object.get('Body')
    except botocore.exceptions.ClientError as error:
        logger.exception(f'Failed to get object in s3 because of {error}')

        raise error


def upload_object(content: list[dict[str, Any]], bucket_name: str, s3_key: str) -> str | bool:
    client = connection.get_client(service_name="s3")
    logger.info(f"Starting file-upload to S3-bucket, with prefix: [{s3_key}]")
    try:
        client.put_object(
            Bucket=bucket_name,
            Body=_format_newline_delimited_json(content),
            Key=s3_key
        )
    except ClientError as error:
        logger.exception(f'Error in uploading file to S3 [{error}]')
        return False

    return s3_key
