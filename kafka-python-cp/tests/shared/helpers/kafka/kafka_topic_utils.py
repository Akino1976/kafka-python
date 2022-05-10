import logging
import operator
from typing import Any

from confluent_kafka.admin import AdminClient, NewTopic

import settings

logger = logging.getLogger(__name__)


def _kafka_topic_exists(topics: list[str], kafka_admin: AdminClient) -> list[bool]:
    kafka_exists = [
        len(kafka_topic.topics) > 0 for topic in topics
        if (kafka_topic := kafka_admin.list_topics(topic=topic))
    ]
    return kafka_exists


def delete_topics():
    kafka_admin = AdminClient({"bootstrap.servers": settings.KAFKA_BROKER})
    meta_data = kafka_admin.list_topics()
    if topics := meta_data.topics:
        topics = [key for (key, value) in topics.items() if operator.contains(key, "events")]
    try:
        fs = kafka_admin.delete_topics(topics, operation_timeout=30)
        for topic, f in fs.items():
            f.result()  # The result itself is None
            logger.info(f"Topic {topics} deleted")
    except Exception:
        pass


def create_topics(topics: str | list[str]):
    kafka_admin = AdminClient({"bootstrap.servers": settings.KAFKA_BROKER})
    if isinstance(topics, str):
        topics = [topics]
    kafka_exists = all(_kafka_topic_exists(topics=topics, kafka_admin=kafka_admin))

    if kafka_exists:
        return None
    new_topics = [NewTopic(topic, num_partitions=3, replication_factor=1) for topic in topics]
    fs = kafka_admin.create_topics(new_topics)
    # Wait for each operation to finish
    for topic, f in fs.items():
        try:
            f.result()  # The result itself is None
            logger.info(f"Topic {topic} created")
        except Exception as error:
            logger.exception(f"Failed to create topic {topic} {error}")


def exclude_magic_bytes(json_body: dict[str, Any]) -> str:
    payload_string = json_body.get("payload")
    json_body |= {"payload": payload_string[7:]}
    return json_body
