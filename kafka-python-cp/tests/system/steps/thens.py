import io
import json
import logging
import operator
from typing import Any

import requests
from pytest_bdd import parsers, then
from types import ModuleType

import helpers.kafka.kafka_topic_utils as kafka_topic_utils
from helpers import aws, comparisons, utils, yaml

logger = logging.getLogger(__file__)


@then(parsers.parse("the function should raise {expected_exception_type}:\n{yaml_string}"))
def should_raise_exception(request: Any, expected_exception_type: str, yaml_string: str):
    options = yaml.load_with_tags(request, yaml_string)
    raised_exception = request.raised_exception
    if error_content := raised_exception.args[0]:
        assert error_content.name() == options.get("name")
        assert error_content.str() == options.get("message")
    assert type(raised_exception).__name__ == expected_exception_type


@then(parsers.parse("another file in S3 like:\n{yaml_string}"))
@then(parsers.parse("there should be a file in S3 like:\n{yaml_string}"))
def get_file_from_bucket(yaml_string: str, request: object):
    options = yaml.load_with_tags(request, yaml_string)
    bucket_name = options.get("bucket")
    expected = options["content"]
    expected_s3_key = options.get("key")
    s3_valid_objects = [
        s3_objects for s3_objects in aws.list_object_names(bucket_name)
        if operator.contains(expected_s3_key, s3_objects)
    ]
    if len(s3_valid_objects) == 0:
        logger.exception("empty s3 bucket")

    if isinstance(s3_valid_objects, list) and len(s3_valid_objects) > 0:
        s3_valid_objects = s3_valid_objects[0]
    decoded_content = aws.get_object(
        bucket_name=bucket_name,
        key=s3_valid_objects
    )
    if operator.contains(s3_valid_objects, "json"):
        decoded_content = decoded_content.decode("utf-8")
        decoded_content = [
            kafka_topic_utils.exclude_magic_bytes(json.loads(row))
            for row in decoded_content.split("\n") if len(row) > 0
        ]
    if (sort_by := options.get("sorted_key")):
        decoded_content = sorted(decoded_content, key=lambda x: x[sort_by], reverse=True)
        expected = sorted(expected, key=lambda x: x[sort_by], reverse=True)
    assert comparisons.contains(decoded_content, expected)
