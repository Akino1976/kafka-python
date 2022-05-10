import logging
import os
from typing import Any

import boto3
import botocore.config

import settings

logger = logging.getLogger(__name__)
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('boto3').setLevel(logging.CRITICAL)


def _get_proxy(service_name: str):
    if (service_proxy := os.getenv("MOCK_AWS_HOST")):
        return service_proxy

    return os.getenv('MOCK_AWS_HOST')


def get_client(service_name: str) -> boto3.session.Session.client:
    proxy = _get_proxy(service_name)

    params = dict(
        service_name=service_name,
        region_name=settings.AWS_REGION,
        config=botocore.config.Config(
            connect_timeout=1,
            read_timeout=10,
            retries={'max_attempts': 5}
        )
    )

    if proxy is not None:
        params['use_ssl'] = proxy.startswith('https://')
        params['config'].proxies = {'http': proxy}

    return boto3.client(**params)
