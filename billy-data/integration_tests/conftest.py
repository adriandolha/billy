import json
import logging
import uuid
from datetime import datetime
from config import load_config
from billy_data.provider import BankStatementProvider
import pytest
import billy_data.app
from billy_data import LOGGER

from billy_data.job import Job, JobStatus
from billy_data.app_context import app_context


@pytest.fixture(scope='session')
def config_valid():
    return load_config()


@pytest.fixture()
def yahoo_config_valid(config_valid):
    return {'user': config_valid['yahoo_user'],
            'password': config_valid['yahoo_password'],
            'host': config_valid['yahoo_host'],
            'port': config_valid['yahoo_port'],
            'card_statement_pdf_password': config_valid['card_statement_pdf_password']
            }


@pytest.fixture(scope='session')
def app_valid(config_valid):
    LOGGER.setLevel(logging.DEBUG)
    app_context.username = config_valid['cognito_user']
    billy_data.app.setup()


@pytest.fixture()
def process_event_valid(app_valid, config_valid):
    return {'op': 'process',
            'username': config_valid['cognito_user'],
            'search_criteria':
                {
                    'subjects':
                        [
                            'Extras de cont Star Gold - Februarie 2022'
                        ],
                    'since': '11-Jul-2021'
                }
            }


@pytest.fixture()
def transform_event_valid(app_valid, config_valid):
    return {'op': 'transform',
            'username': config_valid['cognito_user'],
            'files': [f'{config_valid["cognito_user"]}/bank_statements/raw/bank_statement_4724.pdf']}


@pytest.fixture()
def load_event_valid(app_valid, config_valid):
    return {'op': 'transform',
            'username': config_valid['cognito_user'],
            'files': [f'{config_valid["cognito_user"]}/bank_statements/data/bank_statement_4724_feb_2022.json']}


@pytest.fixture()
def tranform_generated_event_valid(app_valid, config_valid):
    return {'op': 'transform',
            'username': config_valid['cognito_user'],
            'file': '',
            }


@pytest.fixture()
def job_valid(process_event_valid):
    return Job(id=str(uuid.uuid4()),
               created_at=datetime.now(),
               status=JobStatus.CREATED,
               payload=json.dumps(process_event_valid)
               )


@pytest.fixture()
def job_transform_valid(transform_event_valid):
    return Job(id=str(uuid.uuid4()),
               created_at=datetime.now(),
               status=JobStatus.CREATED,
               payload=json.dumps(transform_event_valid)
               )


@pytest.fixture()
def job_load_valid(load_event_valid):
    return Job(id=str(uuid.uuid4()),
               created_at=datetime.now(),
               status=JobStatus.CREATED,
               payload=json.dumps(load_event_valid)
               )


@pytest.fixture()
def test_job_valid(process_event_valid):
    return Job(id='test_job_1',
               created_at=datetime.now(),
               status=JobStatus.CREATED,
               payload=json.dumps({'op': 'test'})
               )


@pytest.fixture()
def bank_statement_provider_valid(config_valid):
    return BankStatementProvider(id=str(uuid.uuid4()),
                                 provider_type='yahoo',
                                 yahoo_user=config_valid.get('yahoo_user'),
                                 yahoo_password=config_valid.get('yahoo_password'),
                                 yahoo_host=config_valid.get('yahoo_host'),
                                 yahoo_port=int(config_valid.get('yahoo_port')),
                                 card_statement_pdf_password=config_valid.get('card_statement_pdf_password'))
