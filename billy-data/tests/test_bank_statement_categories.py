import pandas as pd
from mock import MagicMock
from categories_conftest import *

from billy_data.bank_statements import BankStatementService


class TestBankStatementCategories:
    def test_bank_statements_categories_food(self, temp_file_mock,
                                             bank_statements_mocks,
                                             bank_statements_data_repo,
                                             bank_statement_categories,
                                             categories,
                                             config_valid,
                                             yahoo_config_valid,
                                             card_statements_valid):
        test_file = 'file_test.pdf'
        df = self.transform(temp_file_mock, test_file, yahoo_config_valid, bank_statements_data_repo)
        assert len(df.query("category == 'food' and desc.str.contains('Glovo')")) == 1
        assert len(df.query("category == 'phone' and desc.str.contains('ORANGE')")) == 1

    def transform(self, file_mock, test_file, yahoo_config_valid, bank_statements_data_repo):
        _mock = MagicMock()
        file_mock.return_value.__enter__.return_value = _mock
        _mock.name = test_file
        card_expenses = BankStatementService(**yahoo_config_valid)
        card_expenses.transform(test_file)
        _mock.write.assert_called()
        data_json = bank_statements_data_repo.save.call_args[0][1].decode('utf-8')
        df = pd.read_json(data_json)
        return df
