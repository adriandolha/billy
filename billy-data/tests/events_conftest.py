import json
import uuid
from datetime import datetime

import numpy as np
import pandas as pd
import pytest
from mock import mock, MagicMock

from billy_data.job import JobStatus, Job


@pytest.fixture()
def ddb_job_created_valid():
    return {
        'Records': [
            {
                'eventName': 'INSERT',
                'eventSource': 'aws:dynamodb',
                'dynamodb': {
                    'NewImage': {
                        'result': {'NULL': True},
                        'pk': {'S': 'user#6bda8718-3d36-485c-87c8-72843ba6d84f'},
                        'sk': {'S': 'job#1'},
                        'created_at': {
                            'S': '2022-08-17T17:25:45.122206'
                        },
                        'id': {
                            'S': 'af043020-f8af-42da-8b39-87fb42529618'
                        },
                        'completed_at': {'NULL': True},
                        'payload': {
                            'S': '{"op": "collect", "username": "6bda8718-3d36-485c-87c8-72843ba6d84f", '
                                 '"search_criteria": {"subjects": ["Extras de cont Star Gold - Februarie 2022"], '
                                 '"since": "11-Jul-2021"}}'
                        },
                        'status': {
                            'S': 'CREATED'
                        }
                    }
                }
            }
        ]
    }


@pytest.fixture()
def events_sns_topic():
    with mock.patch('billy_data.events.topic') as _mock:
        yield _mock


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
            'files': ['test_transform.pdf']}


@pytest.fixture()
def load_event_valid(app_valid, config_valid):
    return {'op': 'load',
            'username': config_valid['cognito_user'],
            'files': ['test_load.json', 'test_load1.json']}


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
def sqs_job_created_valid(job_valid):
    body = {'Message': job_valid.to_json(),
            'MessageAttributes': {"event_name": {"Type": "String", "Value": "job.created"}}}
    return {
        'Records': [{
            'body': json.dumps(body),
            'eventSource': 'aws:sqs',
            'eventSourceARN': 'arn:aws:sqs:::billy-data-dev-BillyDataFunctionDataDomainEventQueue',
        }]
    }


@pytest.fixture()
def sqs_job_created_transform_valid(job_transform_valid):
    body = {'Message': job_transform_valid.to_json(),
            'MessageAttributes': {"event_name": {"Type": "String", "Value": "job.created"}}}
    return {
        'Records': [{
            'body': json.dumps(body),
            'eventSource': 'aws:sqs',
            'eventSourceARN': 'arn:aws:sqs:::billy-data-dev-BillyDataFunctionDataDomainEventQueue',
        }]
    }


@pytest.fixture()
def sqs_job_created_load_valid(job_load_valid):
    body = {'Message': job_load_valid.to_json(),
            'MessageAttributes': {"event_name": {"Type": "String", "Value": "job.created"}}}
    return {
        'Records': [{
            'body': json.dumps(body),
            'eventSource': 'aws:sqs',
            'eventSourceARN': 'arn:aws:sqs:::billy-data-dev-BillyDataFunctionDataDomainEventQueue',
        }]
    }
