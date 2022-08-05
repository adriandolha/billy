import pandas as pd
from mock.mock import MagicMock

from billy_data.bank_statements import BankStatementService
from categories_conftest import categories, ddb_table_mock


class TestBankStatementLoad:
    def test_bank_statements_load(self, file_mock,
                                  listdir_mock,
                                  pdf_mock,
                                  pd_read_json,
                                  tabula_mock,
                                  isfile_mock,
                                  bank_statement_df_valid,
                                  categories,
                                  config_valid,
                                  yahoo_config_valid,
                                  card_statements_valid):
        listdir_mock.return_value = ['file1.json', 'file2.csv']
        isfile_mock.return_value = True
        pd_read_json.return_value = bank_statement_df_valid

        bank_statement = BankStatementService(**yahoo_config_valid)
        result = bank_statement.load()

        pd_read_json.assert_called()
        assert result['df_no'] == 2
        assert result['total_bank_statements_entries'] == 50
