import logging
import os
import mock
import pytest

import billy_data.app
from billy_data import LOGGER
from billy_data.bank_statements import create_data_paths


@pytest.fixture(scope='session')
def config_valid():
    import json
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
    billy_data.app.setup()
    return _config


@pytest.fixture()
def yahoo_config_valid(config_valid):
    return {'user': config_valid['yahoo_user'],
            'password': config_valid['yahoo_password'],
            'host': config_valid['yahoo_host'],
            'port': config_valid['yahoo_port'],
            'card_statement_pdf_password': config_valid['card_statement_pdf_password']
            }


@pytest.fixture()
def app_valid(config_valid):
    LOGGER.setLevel(logging.DEBUG)
