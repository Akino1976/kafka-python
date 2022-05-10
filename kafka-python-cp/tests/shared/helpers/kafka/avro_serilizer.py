import base64
import datetime
import json
import os
from typing import Any

import random
from confluent_kafka import avro
from confluent_kafka.avro import CachedSchemaRegistryClient
from confluent_kafka.avro.serializer.message_serializer import MessageSerializer

import settings

SCHEMA_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'schemas'))


def create_avro_file(payload: dict[str, Any],
                     topic: str,
                     json_name: str,
                     kafka_ingested_timestamp: list[int],
                     partition: list[int],
                     offset: list[int]):
    schema_registry_conf = {'url': settings.SCHEMA_REGISTRY_LISTENERS}
    schema_registry_client = CachedSchemaRegistryClient(schema_registry_conf)
    avro_serilizer = MessageSerializer(schema_registry_client)
    json_path = os.path.join(SCHEMA_FOLDER, json_name)
    with open(json_path, "r") as file_connection:
        schema_str = file_connection.read()
    schema_value = avro.loads(schema_str)
    avro_list = [
        {
            "payload": base64.b64encode(avro_data).decode("utf-8"),
            "topic": topic,
            "partition": partition[idx],
            "offset": offset[idx],
            "kafka_ingested_timestamp": kafka_ingested_timestamp[idx],
            "envelope_version": "kc_v1"
        } for (idx, dump) in enumerate(payload) if (avro_data := avro_serilizer.encode_record_with_schema(topic=f"{topic}-value", schema=schema_value, record=dump))
    ]
    return avro_list
