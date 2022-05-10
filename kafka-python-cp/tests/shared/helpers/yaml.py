import importlib
import io
import json
from typing import Any, Type

import yaml

from helpers import utils


def yaml_tag(tag):
    def register_tag(f):
        yaml.Loader.add_multi_constructor(tag, f)

        return f

    return register_tag


def __load_node(loader, node):
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    if isinstance(node, yaml.MappingNode):
        return loader.construct_mapping(node)


def create_loader(request: Any) -> Type:
    return type('RequestLoader', (yaml.Loader, ), {'_pytest_request': request})


def load_with_tags(request: Any, yaml_string: str) -> Any:
    loader = create_loader(request)
    return yaml.load(io.StringIO(yaml_string), Loader=loader)


@yaml_tag("!GetAttribute")
def get_attribute_tag(loader, tag_suffix, node):
    path = __load_node(loader=loader, node=node)
    return utils.get_attribute(path)


@yaml_tag("!Ref")
def get_fixture_tag(loader, tag_suffix, node):
    node = loader.construct_scalar(node)
    return loader._pytest_request.getfixturevalue(node)


@yaml_tag("!SetAttribute")
def set_attribute_tag(loader, tag_suffix, node):
    path, value = tuple(loader.construct_sequence(node, deep=True))
    base, attribute_name = utils.get_module(path)
    setattr(base, attribute_name, value)

    return getattr(base, attribute_name)
