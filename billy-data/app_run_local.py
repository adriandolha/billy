import logging
import os
import json
import sys
from datetime import datetime
from os import listdir
from os.path import isfile, join

from billy_data.bank_statements import create_data_paths, SearchCriteria, BankStatementService, data_paths
from billy_data.repo import DataRepo

LOGGER = logging.getLogger('billy')


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


def yahoo_config(config):
    return {'user': config['yahoo_user'],
            'password': config['yahoo_password'],
            'host': config['yahoo_host'],
            'port': config['yahoo_port'],
            'card_statement_pdf_password': config['card_statement_pdf_password']
            }


def search_criteria_star_gold():
    search_criteria = SearchCriteria()
    search_criterias = ' '.join([search_criteria.subject(['Extras de cont Star Gold - '])])
    return search_criterias


def search_criteria_star_forte():
    search_criteria = SearchCriteria()
    search_criterias = ' '.join([search_criteria.subject(['Extras de cont Star Forte - '])])
    return search_criterias


if __name__ == "__main__":
    config = load_config_to_env()
    LOGGER.setLevel(logging.DEBUG)
    print(LOGGER.level)
    create_data_paths()
    paths = data_paths(DataRepo())
    raw_files_path = paths.raw
    # raw_files = [f for f in listdir(raw_files_path) if isfile(join(raw_files_path, f))]
    raw_files = ['/Users/adriandolha/billy_data/bank_statements/raw/bank_statement_1743.pdf']
    failed_files = []
    print(datetime.now().strftime("%H:%M:%S"))
    for file_name in raw_files:
        print(f'Processing {file_name}...')
        print(datetime.now().strftime("%H:%M:%S"))
        try:
            tf_result = BankStatementService(**yahoo_config(config)).transform(paths.raw_file(file_name))
            print(tf_result)
        except Exception as e:
            failed_files.append(file_name)
            LOGGER.error(e)
            raise e
    print(datetime.now().strftime("%H:%M:%S"))
    print(failed_files)
    # downloaded_files = BankStatement(**yahoo_config(config)).collect(search_criteria_star_forte())
