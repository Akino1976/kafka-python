import logging
import os
from logging.config import dictConfig

import colored

PROJECT_ROOT = os.path.dirname(os.path.abspath("__file__"))
ENVIRONMENT = os.getenv("ENVIRONMENT")
APP_PATH = os.path.dirname(os.path.realpath(PROJECT_ROOT))
APP_NAME = os.getenv("APP_NAME", "validation-service")
APP_COMPONENT = os.getenv("APP_COMPONENT")

logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "[%(asctime)s] - [%(levelname)-3s] - [%(name)-8s] - [%(message)s]",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "colored": {
            "()": "colorlog.ColoredFormatter",
            "format": "[%(blue)s%(asctime)s %(name)-1s %(reset)s] - [%(log_color)s%(levelname)-3s%(reset)s] -"
                      "[%(cyan)s%(message)s%(reset)s]",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "log_colors": {
                "DEBUG": "white",
                "INFO": "bold_green",
                "WARNING": "bold_yellow",
                "ERROR": "bold_red",
                "CRITICAL": "red,bg_white"
            }
        }
    },
    "handlers": {
        "info_file_handler": {
            "level": logging.INFO,
            "filters": None,
            "class": "logging.StreamHandler",
            "formatter": "standard"
        },
        "error_file_handler": {
            "level": logging.ERROR,
            "filters": None,
            "class": "logging.StreamHandler",
            "formatter": "standard"
        }
    },
    "loggers": {
        "root": {
            "handlers": ["info_file_handler"],
            "propagate": True,
            "level": logging.INFO
        }
    }
}
dictConfig(logging_config)

AWS_REGION = os.getenv("AWS_REGION")
SCHEMA_REGISTRY_LISTENERS = os.getenv("SCHEMA_REGISTRY_LISTENERS")
KAFKA_BROKER = os.getenv("KAFKA_BROKER")
S3_EXPORT_BUCKET = os.getenv("S3_EXPORT_BUCKET")
