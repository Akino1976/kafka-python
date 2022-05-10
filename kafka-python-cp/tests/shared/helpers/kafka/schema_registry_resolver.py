import json
import operator
import os

from confluent_kafka.schema_registry import Schema, SchemaRegistryClient

import helpers.utils as utils
import settings

SCHEMA_REGISTRY_LISTENERS = os.getenv("SCHEMA_REGISTRY_LISTENERS")
SCHEMA_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'schemas'))


def delete_subject() -> bool:
    if not operator.eq(settings.ENVIRONMENT, "docker"):
        raise Exception("Not applicable on testing/production environment exit")
        return None
    connection_configuration: dict = {"url": SCHEMA_REGISTRY_LISTENERS}
    schema_registry_client = SchemaRegistryClient(connection_configuration)
    for subject in schema_registry_client.get_subjects():
        schema_registry_client.delete_subject(subject_name=subject, permanent=True)


def upload_schema(topic_name: str, folder: str) -> bool:
    if not operator.eq(settings.ENVIRONMENT, "docker"):
        raise Exception("Not applicable on testing/production environment exit")
        return None
    topic_name = f"{topic_name}-value" if not topic_name.endswith("value") else topic_name
    connection_configuration: dict = {'url': SCHEMA_REGISTRY_LISTENERS}
    schema_registry_client = SchemaRegistryClient(connection_configuration)
    folder_path = os.path.join(SCHEMA_FOLDER, folder)
    schema_paths = utils.get_all_files(directory=folder_path, file_regexp='*avsc')
    for schema_path in schema_paths:
        try:
            with open(schema_path, "r") as file_connection:
                schema_str = file_connection.read()
            schema: Schema = Schema(schema_str=schema_str, schema_type="AVRO")
            schema_registry_client.register_schema(subject_name=topic_name, schema=schema)
        except Exception as error:
            raise error
    subjects = schema_registry_client.get_subjects()
    return True if len(subjects) > 0 else False
