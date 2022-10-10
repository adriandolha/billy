import logging
import os
import json
import sys
from datetime import datetime
from os import listdir
from os.path import isfile, join


def load_config_to_env():
    global _config, k, v
    config_file = f"{os.path.expanduser('~')}/.cloud-projects/billy-local-integration.json"
    print(f'Config file is {config_file}')
    if os.path.exists(config_file):
        with open(config_file, "r") as _file:
            _config = dict(json.load(_file))
            for k, v in _config.items():
                os.environ[k] = str(v)
    else:
        _config = os.environ
    os.environ['prometheus_metrics'] = 'False'
    print('Config...')
    print(_config)
    return _config


load_config_to_env()

from billy_api.demo import configure_demo_user
from billy_api.config import CONFIG

if __name__ == "__main__":
    configure_demo_user(CONFIG['demo_user'], CONFIG['demo_user_password'])



