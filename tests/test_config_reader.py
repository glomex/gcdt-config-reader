# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import json
import os
import logging

import pytest

from gcdt_config_reader.config_reader import read_config_if_exists, _read_python_cfg, \
    _read_json_cfg, read_config
from gcdt_config_reader import config_reader
from . import here


def read(filename):
    with open(filename, 'r') as cfile:
        cfg = json.load(cfile)
    return cfg


@pytest.fixture(scope='function')  # 'function' or 'module'
def sample_python_cfg_folder():
    # helper to get into the sample folder so kumo can find cloudformation.py
    cwd = (os.getcwd())
    os.chdir(here('./resources/sample_python_cfg/'))
    yield
    # cleanup
    os.chdir(cwd)  # cd back to original folder


@pytest.fixture(scope='function')  # 'function' or 'module'
def sample_lambda_with_setting_folder():
    # helper to get into the sample folder so kumo can find cloudformation.py
    cwd = (os.getcwd())
    os.chdir(here('./resources/sample_lambda_with_setting/'))
    yield
    # cleanup
    os.chdir(cwd)  # cd back to original folder


def test_read_config(sample_lambda_with_setting_folder):
    expected = read(here('./resources/sample_lambda_with_setting/expected_gcdt_dev.json'))
    config = {}
    read_config(({'env': 'dev'}, config))

    assert config == expected


def test_conflicting_configs(sample_python_cfg_folder, caplog):
    expected = read(here('./resources/sample_python_cfg/expected_gcdt_dev.json'))
    actual = read_config_if_exists('gcdt', 'dev')

    assert actual == expected
    assert caplog.record_tuples == [
        (config_reader.__name__, logging.WARNING,
         'found multiple types of config files: [\'gcdt_dev.py\', \'gcdt_dev.json\']'),
    ]


def test_read_json_config():
    expected = read(here('./resources/sample_lambda_with_setting/expected_gcdt_dev.json'))
    actual = _read_json_cfg(here('./resources/sample_lambda_with_setting/gcdt_dev.json'))

    assert actual == expected


def test_read_python_config():
    expected = read(here('./resources/sample_python_cfg/expected_gcdt_dev.json'))

    actual = _read_python_cfg(here('./resources/sample_python_cfg/gcdt_dev.py'))

    assert actual == expected

