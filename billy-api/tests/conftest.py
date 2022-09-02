import json
import logging
import os
from unittest.mock import MagicMock

import boto3
import pandas as pd
import pytest
from mock import mock

from billy_api import LOGGER
from billy_api.auth import User, Groups


@pytest.fixture(scope='session')
def config_valid():
    import json
    config_file = f"{os.path.expanduser('~')}/.cloud-projects/billy-local-integratin.json"
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
def data_ddb_mock():
    _mock = MagicMock()
    with mock.patch('billy_api.bank_statements.ddb', _mock):
        yield _mock


@pytest.fixture()
def data_mock(data_ddb_mock):
    with mock.patch('billy_api.bank_statements.S3DataRepo') as _mock:
        yield _mock


@pytest.fixture()
def auth_requests():
    with mock.patch('billy_api.auth.requests') as _requests:
        yield _requests


@pytest.fixture()
def user_valid(auth_requests, auth_service_mock, jwk_mock):
    with mock.patch('billy_api.auth.jwt') as _jwt:
        _jwt.decode.return_value = {'cognito:username': 'adolha', 'cognito:groups': ['Users']}
        auth_requests.post.return_value.content = json.dumps({'id_token': 'id_token'}).encode('utf-8')

        auth_service_mock.get_user.return_value = User(username='adolha', group=Groups.USERS.value)
        yield _jwt


@pytest.fixture()
def verified_user_valid(auth_requests, auth_service_mock, jwk_mock):
    with mock.patch('billy_api.auth.jwt') as _jwt:
        _jwt.decode.return_value = {'cognito:username': 'adolha', 'cognito:groups': ['VerifiedUsers']}
        auth_requests.post.return_value.content = json.dumps({'id_token': 'id_token'}).encode('utf-8')

        auth_service_mock.get_user.return_value = User(username='adolha', group=Groups.VERIFIED_USERS.value)
        yield _jwt


@pytest.fixture()
def jwk_mock(auth_requests):
    with mock.patch('billy_api.auth.jwk') as _jwk:
        yield _jwk


@pytest.fixture()
def auth_service_mock(auth_requests):
    with mock.patch('billy_api.auth.auth_service') as _mock:
        yield _mock


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
        ['2022-06-12', 'Schimb valutar r123', '-1.0', 'other'],
        ['2022-06-12', 'Incasare OP', '-1.0', 'other'],
        ['2022-06-12', 'Transfer intern', '-1.0', 'other'],
        ['2022-06-12', 'P2P BTPay r123', '-1.0', 'other'],
        ['2022-06-12', 'Debitare automata carduri de credit', '-1.0', 'other'],
    ]
    with mock.patch('billy_api.stats.get_data_df') as _mock:
        df = pd.DataFrame(data=_data, columns=['date', 'desc', 'suma', 'category'])
        df['suma'] = df['suma'].astype(float)
        _mock.return_value = df
        yield _data


@pytest.fixture()
def job_request_valid():
    return {
        'payload': json.dumps({
            'op': 'test',
            'attribute': 'attr'
        })
    }


@pytest.fixture()
def category_request_valid():
    return {
        'name': 'test_category',
        'key_words': ['key_word1']
    }
