import importlib

import unittest.mock as mock


def create_mock(monkeypatch, attribute_path, configuration):
    returns = None
    if "returns" not in configuration:
        raise Exception('Need to have a return value')

    returns = configuration['returns']
    mocked_attribute = mock.MagicMock(return_value=returns)
    module_path, attribute_name = attribute_path.rsplit('.', 1)
    object_to_mock = importlib.import_module(module_path)

    monkeypatch.setattr(object_to_mock, attribute_name, mocked_attribute)
