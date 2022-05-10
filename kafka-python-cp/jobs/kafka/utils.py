import logging
import uuid

from confluent_kafka.schema_registry import SchemaRegistryClient

logger = logging.getLogger(__name__)


def get_last_registry(topic: str, schema_registry: SchemaRegistryClient) -> dict[str, str]:
    topic = f"{topic}-value" if not topic.endswith("value") else topic
    try:
        schema = schema_registry.get_latest_version(subject_name=topic)
    except Exception:
        logger.error(f"no topic with name {topic}")
    return {
        "version": schema.version,
        "schema_id": schema.schema_id,
        "schema": schema.schema.schema_str
    }


def delivery_report(error, message):
    if error is not None:
        logger.error(f"Delivery failed for record {message.key()}: {error}")
        return None
    log = f"Record {message.key()} successfully produced to {message.topic()} [{message.partition()}] at offset {message.offset()}"
    print(log)
    logger.info(log)


def get_uuid():
    return str(uuid.uuid4())
