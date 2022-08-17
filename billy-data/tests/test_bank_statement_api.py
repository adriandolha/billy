import json
import os

import pandas as pd
from mock import MagicMock
from events_conftest import collect_event_valid, transform_event_valid
import app
from billy_data.bank_statements import BankStatementService, SearchCriteria, data_paths, BankStatementEntry
from billy_data.repo import data_repo

os.environ['env'] = 'test'


class TestBankStatementApi:
    def test_bank_statement_collect(self, file_mock, config_valid, yahoo_config_valid, card_statements_valid,
                                    collect_event_valid, bank_statements_data_repo):
        bank_statements_data_repo.save.return_value = 'test_file.json'
        response = app.lambda_handler(collect_event_valid, [])
        assert response['statusCode'] == 200
        result = json.loads(response['body'])
        downloaded_files = result['downloaded_files']
        bank_statements_data_repo.save.assert_called()
        assert collect_event_valid['username'] in bank_statements_data_repo.save.call_args[0][0]
        assert downloaded_files[0] == 'test_file.json'

    def test_bank_statement_transform(self, file_mock, pdf_mock, tabula_mock, config_valid, yahoo_config_valid,
                                      card_statements_valid,
                                      transform_event_valid, bank_statements_data_repo):
        bank_statements_data_repo.save.return_value = 'test_file.json'
        response = app.lambda_handler(transform_event_valid, [])
        assert response['statusCode'] == 200
        result = json.loads(response['body'])
        downloaded_files = result['downloaded_files']
        bank_statements_data_repo.save.assert_called()
        assert downloaded_files[0] == 'test_file.json'
