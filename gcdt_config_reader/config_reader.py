# -*- coding: utf-8 -*-
"""A gcdt-plugin which demonstrates how to implement hello world as plugin."""
from __future__ import unicode_literals, print_function
import os
import imp
import json

from gcdt import gcdt_signals
from gcdt.utils import dict_merge
from gcdt.gcdt_logging import getLogger
from gcdt.gcdt_signals import check_hook_mechanism_is_intact, \
    check_register_present
from gcdt.gcdt_defaults import CONFIG_READER_CONFIG
from gcdt.utils import GracefulExit


log = getLogger(__name__)
CONFIG_BASE_NAME = 'gcdt'


def _load_module(path):
    """Load module from path.

    :param path: Absolute or relative path to module.
    :return: module
    """
    module = imp.load_source(os.path.splitext(os.path.basename(path))[0], path)
    return module


def _check_generate_config_present(module):
    # helper
    if hasattr(module, 'generate_config'):
        return True


def _read_json_cfg(filename):
    # helper
    with open(filename, 'r') as jfile:
        return json.load(jfile)


def _read_python_cfg(filename):
    # helper
    # TODO docu!
    # we assume that you have a method like this so we can read the config:
    # def generate_config():
    #    return config_dict
    cfg = _load_module(filename)
    if not _check_generate_config_present(cfg):
        log.warning('Can not read config file \'%s\'. generate_config() is missing!', filename)
        return {}
    if not check_hook_mechanism_is_intact(cfg):
        log.warning('No valid hook configuration: \'%s\'. Not using hooks!', filename)
    else:
        if check_register_present(cfg):
            cfg.register()   # register the plugin so it listens to gcdt_signals
    return cfg.generate_config()


def read_config_if_exists(config_base_name, env):
    """If config file exists, read it and return the config.
    :param config_base_name:
    :param env:
    :return:
    """
    cfg_files = []
    for f in ['%s_%s.%s' % (config_base_name, env, ext) for ext in
              ['py', 'json', 'yaml']]:
        if os.path.exists(f):
            cfg_files.append(f)

    if len(cfg_files) == 0:
        return {}
    elif len(cfg_files) > 1:
        log.warning('found multiple types of config files: %s' %
                    [str(cf) for cf in cfg_files])
    # take the first one
    filename = cfg_files[0]
    if filename.endswith('.py'):
        return _read_python_cfg(filename)
    elif filename.endswith('.json'):
        return _read_json_cfg(filename)
    elif filename.endswith('.yaml'):
        # TODO check for PyYaml module and read the yaml cfg file!
        pass


def read_ignore_files(ignorefiles):
    gcdtignore = []
    for p in ignorefiles:
        if os.path.exists(p):
            with open(p, 'r') as ifile:
                gcdtignore.extend(ifile.read().splitlines())
    return gcdtignore


def read_config(params):
    """Read config from file.
    :param params: context, config (context - the _awsclient, etc..
                   config - The stack details, etc..)
    """
    context, config = params
    try:
        cfg = read_config_if_exists(CONFIG_BASE_NAME, context['env'])
        if cfg:
            # apply the gcdt_plugins_commons DEFAULT_CONFIG
            dict_merge(config, CONFIG_READER_CONFIG)
            dict_merge(config, cfg)
            gcdtignore = read_ignore_files(
                # TODO: make it configurable in DEFAULT_CONFIG
                ['~/.ramudaignore', '.gcdtignore', '.npmignore']
            )
            if gcdtignore:
                dict_merge(config, {'gcdtignore': gcdtignore})
    except GracefulExit:
        raise
    except Exception as e:
        config['error'] = e.message


def register():
    """Please be very specific about when your plugin needs to run and why.
    E.g. run the sample stuff after at the very beginning of the lifecycle
    """
    gcdt_signals.config_read_init.connect(read_config)


def deregister():
    gcdt_signals.config_read_init.disconnect(read_config)
