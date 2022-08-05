import pandas as pd
from mock import MagicMock
from categories_conftest import *

from billy_data.bank_statements import BankStatementService


class TestBankStatementCategories:
    def test_bank_statements_categories_food(self, file_mock,
                                             pdf_mock,
                                             tabula_mock,
                                             bank_statement_categories,
                                             categories,
                                             config_valid,
                                             yahoo_config_valid,
                                             card_statements_valid):
        test_file = 'file_test.pdf'
        df = self.transform(file_mock, test_file, yahoo_config_valid)
        assert len(df.query("category == 'food' and desc.str.contains('Glovo')")) == 1
        assert len(df.query("category == 'phone' and desc.str.contains('ORANGE')")) == 1

    def transform(self, file_mock, test_file, yahoo_config_valid):
        _mock = MagicMock()
        file_mock.return_value.__enter__.return_value = _mock
        card_expenses = BankStatementService(**yahoo_config_valid)
        card_expenses.transform(test_file)
        _mock.write.assert_called()
        df = pd.read_json(_mock.write.call_args[0][0].decode('utf-8'))
        return df
