import json
import logging
import os
from typing import Any

import click

import common.storage as storage
import settings
from kafka import consumer, producer, utils

logger = logging.getLogger(__name__)


@click.group()
def cli():
    pass


@cli.command()
@click.option("--dataset", default=None)
@click.option("--topic", default=None)
@click.option("--kafka_topic", default=None)
def producer_handler(dataset: dict[str, Any], topic: str, kafka_topic: str):
    logger.info(f"{topic}")
    if isinstance(dataset, str):
        dataset = json.loads(dataset)
    try:
        producer.processor(
            dataset=dataset.get("payload"),
            topic=topic,
            kafka_topic=kafka_topic
        )
    except Exception as error:
        logger.exception(f"Event not processed [{error}]")

        raise error

    logger.info("Successfully processed event")


@cli.command()
@click.option("--topic", default=None)
@click.option("--kafka_topic", default=None)
def consumer_handler(topic: str, kafka_topic: str):
    logger.info(f"{topic}")
    try:
        dataset = consumer.processor(
            topic=topic,
            kafka_topic=kafka_topic
        )
    except Exception as error:
        logger.exception(f"Event not processed [{error}]")

        raise error
    logger.info("Successfully processed event")
    s3_key = storage.upload_object(
        content=dataset,
        bucket_name=settings.S3_EXPORT_BUCKET,
        s3_key=f"silos/kafka/{topic}-{utils.get_uuid()}.json.gz"
    )
    return s3_key


if __name__ == "__main__":
    cli()
