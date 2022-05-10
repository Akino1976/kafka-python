import importlib
import logging
from typing import Any

import requests
from click.testing import CliRunner
from pytest_bdd import parsers, when
from types import ModuleType

from helpers import yaml

logger = logging.getLogger(__file__)


@when(parsers.parse("I call the {callable_path} function with parameters:{yaml_string}"))
def call_invoke_callable(request: Any, callable_path: str, yaml_string: Any):
    paramters = yaml.load_with_tags(request, yaml_string)
    if isinstance(paramters, dict):
        paramters = [f"{key}={value}" for (key, value) in paramters.items()]

    variable_path, variable_method_name = callable_path.rsplit(".", 1)
    object_enviroment = importlib.import_module(variable_path)

    callable_function = getattr(object_enviroment, variable_method_name)

    process = CliRunner().invoke(callable_function, paramters)
    if exception := process.exception:
        request.raised_exception = exception
    else:
        request.process = process
