import base64
import datetime
import logging
import time
from typing import Any

from confluent_kafka import (
    avro,
    DeserializingConsumer,
    KafkaError,
    KafkaException,
)
from confluent_kafka.avro import CachedSchemaRegistryClient
from confluent_kafka.avro.serializer.message_serializer import MessageSerializer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import StringDeserializer

import kafka.utils as utils
import settings

# Kafka environment variables
KAFKA_BROKER = settings.KAFKA_BROKER
logger = logging.getLogger(__name__)


def _create_avro_file(dataset: list[dict[str, Any]],
                      schema_json: str) -> list[dict[str, Any]]:
    schema_registry_client = CachedSchemaRegistryClient({"url": settings.SCHEMA_REGISTRY_LISTENERS})
    avro_serilizer = MessageSerializer(schema_registry_client)
    avro_list = [
        {
            "payload": base64.b64encode(avro_data).decode("utf-8"),
            "topic": dump.get("topic"),
            "partition": dump.get("partition"),
            "offset": dump.get("offset"),
            "kafka_ingested_timestamp": dump.get("timestamp"),
            "envelope_version": dump.get("key")
        } for (idx, dump) in enumerate(dataset)
        if (avro_data := avro_serilizer.encode_record_with_schema(topic=dump.get("topic"), schema=schema_json, record=dump.get("value")))
    ]
    return avro_list


def repr_message(message: Any):
    return {
        "topic": message.topic(),
        "key": message.key(),
        "offset": message.offset(),
        "timestamp": message.timestamp()[-1] / 1000,
        "partition": message.partition(),
        "value": message.value()
    }


def processor(topic: str, kafka_topic: str):
    output = []
    schema_registry_client = SchemaRegistryClient({"url": settings.SCHEMA_REGISTRY_LISTENERS})
    schema = utils.get_last_registry(topic=topic, schema_registry=schema_registry_client)
    schema_str = schema.get("schema")
    avro_deserializer = AvroDeserializer(schema_registry_client=schema_registry_client, schema_str=schema_str)
    CONSUMER_CONF = {
        'bootstrap.servers': KAFKA_BROKER,
        'key.deserializer': StringDeserializer("utf_8"),
        'value.deserializer': avro_deserializer,
        'group.id': "connect1-group",
        'auto.offset.reset': "earliest"
    }
    consumer = DeserializingConsumer(CONSUMER_CONF)
    consumer.subscribe([kafka_topic])
    try:
        while True:
            message = consumer.poll(timeout=5)
            if message is None:
                break
            if error := message.error():
                if error.code() == KafkaError._PARTITION_EOF:
                    break
                else:
                    raise KafkaException(error)
            consumer.commit(asynchronous=False)
            dataset = repr_message(message=message)
            if dataset is not None:
                output.append(dataset)
    except Exception as error:
        # Report malformed record, discard results, continue polling
        logger.error(f"Message deserialization failed {error}")
    finally:
        consumer.close()
    avro_data = _create_avro_file(
        dataset=output,
        schema_json=avro.loads(schema_str)
    )
    return avro_data
