import logging
from typing import Any

from confluent_kafka import avro, SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import StringSerializer

import kafka.utils as utils
import settings

# Kafka environment variables
KAFKA_BROKER = settings.KAFKA_BROKER
logger = logging.getLogger(__name__)


def processor(dataset: list[dict[str, Any]], topic: str, kafka_topic: str) -> int:
    schema_registry_conf = {"url": settings.SCHEMA_REGISTRY_LISTENERS}
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)
    schema = utils.get_last_registry(topic=topic, schema_registry=schema_registry_client)
    schema_str = schema.get("schema")
    avro_serializer = AvroSerializer(
        schema_registry_client=schema_registry_client,
        schema_str=schema_str,
        conf={"auto.register.schemas": False}
    )
    PRODUCER_CONF = {
        "bootstrap.servers": KAFKA_BROKER,
        "key.serializer": StringSerializer("utf_8"),
        "value.serializer": avro_serializer
    }
    avro_producer = SerializingProducer(PRODUCER_CONF)
    for value in dataset:
        try:
            avro_producer.produce(
                topic=kafka_topic,
                key=utils.get_uuid(),
                value=value,
                on_delivery=utils.delivery_report
            )
        except ValueError as error:
            logger.error(f"{error}")
            print("Invalid input, discarding record...")
            print("\nFlushing records...")
    producer_message = avro_producer.flush(timeout=5)

    return producer_message
