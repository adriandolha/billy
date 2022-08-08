import logging
import os
import pytest
import boto3

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


@pytest.fixture(scope='session')
def api_url(config_valid):
    return config_valid['api_url']


@pytest.fixture(scope='session')
def id_token(config_valid):
    client = boto3.client('cognito-idp')
    response = client.initiate_auth(
        ClientId=config_valid['cognito_client_id'],
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={"USERNAME": config_valid['cognito_user'],
                        "PASSWORD": config_valid['cognito_user_password']},
    )
    LOGGER.debug(response)
    id_token = response["AuthenticationResult"]["IdToken"]
    print(f'Cognito id token {id_token}')
    return id_token
