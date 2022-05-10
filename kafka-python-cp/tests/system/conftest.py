import contextlib
import os
import time

import requests

import settings


def pytest_sessionstart(session):
    """ Sleeps for up to 60 seconds before session.main() is called. """
    for i in range(0, 120):
        print(
            "Waiting for schema-registry to start: {seconds} seconds waited"
            .format(seconds=(i / 2))
        )
        with contextlib.suppress(Exception):
            response = requests.get(os.getenv("SCHEMA_REGISTRY_LISTENERS"))
            if response.ok:
                print("Waited {seconds} seconds for schema-registry to start".format(seconds=(i / 2)))
                break

        time.sleep(.5)
