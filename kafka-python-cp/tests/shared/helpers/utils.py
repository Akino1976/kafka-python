import builtins
import contextlib
import importlib
import json
import os
from glob import glob
from typing import Any, Optional

from types import ModuleType


def get_all_files(directory: str, file_regexp: str = "*") -> list[str]:
    if os.path.exists(directory) is False:
        raise Exception(f'Directory dont exists {directory}')

    else:
        all_files = [
            base_path for filepath in os.walk(directory)
            for base_path in glob(os.path.join(filepath[0], file_regexp))
            if os.path.isfile(base_path)
        ]
    all_files.sort()
    return all_files


def get_attribute(path: str) -> str | bool:
    with contextlib.suppress(ImportError):
        module_path, attribute, *rest = path.rsplit('.', 1)
        module = importlib.import_module(module_path)
        if hasattr(module, attribute):
            return getattr(module, attribute)
    return False


def format_newline_delimited_json(records: list[dict[str, Any]]) -> str:
    return "\n".join([json.dumps(record, ensure_ascii=False) for record in records if record])


def get_module(path: str) -> tuple[ModuleType, str]:
    module = builtins
    module_path = ''

    with contextlib.suppress(ImportError):
        num_dots = len(path.split('.'))

        for num_dots in reversed(range(num_dots)):
            possible_module_path = path.rsplit(".", num_dots)[0]
            module = importlib.import_module(possible_module_path)
            module_path = possible_module_path

            print("Module path: '{}'".format(module_path))

    rest_path = path.replace(module_path, '').strip('.')

    return module, rest_path
