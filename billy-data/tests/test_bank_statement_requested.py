import os
from mock import MagicMock

from billy_data.bank_statements import BankStatementService, data_paths
import pandas

os.environ['env'] = 'test'


class TestBankStatementRequested:
    def test_bank_statements_transform_valid(self, temp_file_mock, tabula_mock, bank_statement_requested_valid,
                                             yahoo_config_valid, bank_statements_data_repo,
                                             card_statements_valid, bank_statements_mocks):
        _mock = MagicMock()
        temp_file_mock.return_value.__enter__.return_value = _mock
        _mock.name = 'file_test.csv'
        card_expenses = BankStatementService(**yahoo_config_valid)
        tf_files = card_expenses.transform('file_test.pdf')
        paths = data_paths(bank_statements_data_repo)
        assert tabula_mock.convert_into.call_args[0][1] == 'file_test.csv'
        assert tf_files['file_no_pass'] == paths.no_pass_file('file_test.pdf')
        assert tf_files['file_tables'] == paths.tables_file('file_test.csv')
        assert tf_files['file_data'] == paths.data_file('file_test_Jul_2021.json')
        _mock.write.assert_called()
        data_json = bank_statements_data_repo.save.call_args[0][1].decode('utf-8')
        df = pandas.read_json(data_json)
        assert len(df) == 9
        assert df['suma'].sum() == -2629.75

    def test_bank_statements_transform_first_entry(self, file_mock, pdf_mock,
                                                   tabula_mock,
                                                   bank_statement_requested_valid,
                                                   config_valid,
                                                   yahoo_config_valid,
                                                   card_statements_valid):
        test_file = 'file_test.pdf'
        df = self.transform(file_mock, test_file, yahoo_config_valid)
        # print(df.to_string())
        assert len(df.query("date == '2021-07-07' and suma == -31.00 and desc.str.contains('RCS')")) == 1

    def test_bank_statements_transform_day_with_multiple_entries(self, file_mock, pdf_mock,
                                                                 tabula_mock,
                                                                 bank_statement_requested_valid,
                                                                 config_valid,
                                                                 yahoo_config_valid,
                                                                 card_statements_valid):
        test_file = 'file_test.pdf'
        df = self.transform(file_mock, test_file, yahoo_config_valid)
        # print(df.to_string())
        assert len(df.query("date == '2021-07-07' and suma == -21.27 and desc.str.contains('GAZ')")) == 1

    def test_bank_statements_transform_last_entry_not_missing(self, file_mock, pdf_mock,
                                                              tabula_mock,
                                                              bank_statement_requested_valid,
                                                              config_valid,
                                                              yahoo_config_valid,
                                                              card_statements_valid):
        test_file = 'file_test.pdf'
        df = self.transform(file_mock, test_file, yahoo_config_valid)
        print(df.to_string())
        assert len(df.query("date == '2021-07-31' and suma == -5.0 and desc.str.contains('Abonament BT')")) == 1

    def test_bank_statements_transform_credit_is_positive(self, file_mock, pdf_mock,
                                                          tabula_mock,
                                                          bank_statement_requested_valid,
                                                          config_valid,
                                                          yahoo_config_valid,
                                                          card_statements_valid):
        test_file = 'file_test.pdf'
        df = self.transform(file_mock, test_file, yahoo_config_valid)
        print(df.to_string())
        assert len(df.query("date == '2021-07-15' and suma == 11.10 and desc.str.contains('Incasare OP')")) == 1

    def transform(self, file_mock, test_file, yahoo_config_valid):
        _mock = MagicMock()
        file_mock.return_value.__enter__.return_value = _mock
        card_expenses = BankStatementService(**yahoo_config_valid)
        card_expenses.transform(test_file)
        _mock.write.assert_called()
        df = pd.read_json(_mock.write.call_args[0][0].decode('utf-8'))
        return df
