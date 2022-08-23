from integration_tests.config import load_config

import logging
import os
import pytest
import boto3

from billy_api import LOGGER, app
from billy_api.auth import id_token_for_client_credentials


@pytest.fixture(scope='session')
def config_valid():
    LOGGER.setLevel(logging.DEBUG)
    _config = load_config()
    app.setup()
    return _config


@pytest.fixture(scope='session')
def api_url(config_valid):
    return config_valid['api_url']


@pytest.fixture(scope='session')
def id_token(config_valid):
    return id_token_for_client_credentials(config_valid['cognito_user'], config_valid['cognito_user_password'],
                                           config_valid['cognito_client_id'])
