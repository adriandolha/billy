import json
import logging
import os
import boto3
import pandas as pd
import pytest
from mock import mock

from billy_api import LOGGER


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
    LOGGER.setLevel(logging.DEBUG)
    return _config


@pytest.fixture()
def data_mock():
    with mock.patch('billy_api.bank_statements.S3DataRepo') as _mock:
        yield _mock


@pytest.fixture()
def auth_requests():
    with mock.patch('billy_api.auth.requests') as _requests:
        yield _requests


@pytest.fixture()
def user_valid(auth_requests):
    with mock.patch('billy_api.auth.jwt') as _jwt:
        _jwt.decode.return_value = {'cognito:username': 'adolha'}
        yield _jwt


@pytest.fixture()
def data_valid(data_mock):
    data = [
        ['2022-04-21', 'Glovo entr1', '-1.0', 'food'],
        ['2022-04-11', 'Glovo entr1', '-1.0', 'food'],
        ['2022-04-22', 'Glovo test entr1', '-1.0', 'food'],
        ['2022-04-12', 'Glovo entr1', '-1.0', 'food'],
    ]
    data_mock.return_value.get.return_value = pd.DataFrame(data=data,
                                                           columns=['date', 'desc', 'suma', 'category']).to_json()
    yield data_valid


@pytest.fixture()
def stats_valid(data_mock):
    _data = [
        ['2022-04-21', 'Glovo entr1', '-1.0', 'food'],
        ['2022-04-11', 'Glovo entr1', '-1.0', 'food'],
        ['2022-04-22', 'Glovo entr1', '-1.0', 'food'],
        ['2022-04-12', 'Glovo entr1', '-1.0', 'food'],
        ['2022-05-11', 'Glovo entr1', '-1.0', 'food'],
        ['2022-05-12', 'Apple entr1', '-1.0', 'phone'],
        ['2022-05-12', 'Airbnb entr1', '-1.0', 'travel'],
        ['2022-06-12', 'Orange entr1', '-1.0', 'phone'],
        ['2022-06-14', 'Orange entr1', '-1.0', 'phone'],
        ['2022-06-12', 'Gas entr1', '-1.0123456', 'gas'],
        ['2022-06-12', 'Glovo entr1', '-1.0', 'food'],
    ]
    with mock.patch('billy_api.stats.get_data_df') as _mock:
        df = pd.DataFrame(data=_data, columns=['date', 'desc', 'suma', 'category'])
        df['suma'] = df['suma'].astype(float)
        _mock.return_value = df
        yield _data
