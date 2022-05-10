import json
from collections.abc import Callable
from typing import Any

from pytest_bdd import given, parsers

from helpers import aws, mocks, utils, yaml
from helpers.kafka import (
    avro_serilizer,
    kafka_topic_utils,
    schema_registry_resolver,
)


@given(parsers.parse("the bucket {bucket_name} is empty"))
def empty_bucket(request: Any, bucket_name: str):
    bucket_name = yaml.load_with_tags(request, bucket_name)
    aws.empty_bucket(bucket_name)


@given(parsers.parse("the mocks:\n{yaml_string}"))
def define_mocks(request: Any, monkeypatch: "MonkeyPatch", yaml_string: dict[str, Any]):
    yaml_string = yaml.load_with_tags(request, yaml_string)
    for (method_path, configuration) in yaml_string.items():
        mocks.create_mock(monkeypatch, method_path, configuration)


@given(parsers.parse("all topics is deleted"))
def delete_topic():
    schema_registry_resolver.delete_subject()


@given(parsers.parse("a topic in schema-registry as:\n{yaml_string}"))
def create_topic(request: Any, yaml_string: str):
    yaml_string = yaml.load_with_tags(request, yaml_string)
    schema_registry_resolver.upload_schema(**yaml_string)


@given(parsers.parse("the parameters:\n{yaml_string}"), target_fixture="parameters")
def create_parameters(request: Any, yaml_string: dict[str, Any]) -> dict[str, Any]:
    return yaml.load_with_tags(request, yaml_string)


@given(parsers.parse("the values:\n{yaml_string}"))
def create_values(request: Any, yaml_string: Any) -> None:
    yaml.load_with_tags(request, yaml_string)
    pass


@given(parsers.parse("a dataset as like:\n{yaml_string}"), target_fixture="json_dump")
def create_avro(request: Any, yaml_string: Any):
    yaml_string = yaml.load_with_tags(request, yaml_string)
    return json.dumps(yaml_string)


@given(parsers.parse("kafka topic {kafka_topic} is {purpose}"))
def kafka_topic(request: Any, kafka_topic: str, purpose: str):
    match purpose:
        case "deleted":
            caller: Callable = getattr(kafka_topic_utils, "delete_topics")
            caller()
        case "created":
            caller: Callable = getattr(kafka_topic_utils, "create_topics")
            caller(topics=kafka_topic)
