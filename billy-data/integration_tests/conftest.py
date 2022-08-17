import logging
import os
import pytest


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
    import billy_data.app
    from billy_data import LOGGER

    LOGGER.setLevel(logging.DEBUG)
    billy_data.app.setup()


@pytest.fixture()
def collect_event_valid():
    return {'op': 'collect',
            'username': 'test_user', 'search_criteria':
                {
                    'subjects':
                        [
                            'Extras de cont Star Gold - Februarie 2022'
                        ],
                    'since': '11-Jul-2021'
                }
            }


@pytest.fixture()
def transform_event_valid():
    return {
        'op': 'transform',
        'username': 'test_user',
        'file': 'test_file.json'
    }


@pytest.fixture()
def tranform_generated_event_valid():
    return {'op': 'transform',
            'username': 'test_user',
            'file': '',
            }
