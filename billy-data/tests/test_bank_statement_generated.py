import os

import pandas as pd
from mock import MagicMock

from billy_data.bank_statements import BankStatementService, SearchCriteria, data_paths, BankStatementEntry
from billy_data.repo import DataRepo

os.environ['env'] = 'test'


class TestBankStatementGenerated:
    def test_bank_statement_collect(self, file_mock, config_valid, yahoo_config_valid, card_statements_valid):
        _mock = MagicMock()
        file_mock.return_value.__enter__.return_value = _mock
        card_expenses = BankStatementService(**yahoo_config_valid)
        downloaded_files = card_expenses.collect(
            SearchCriteria().subject(['Extras de cont Star Gold - Aprilie 2022']))
        raw_file = data_paths(DataRepo()).raw_file('bank_statement_100.pdf')
        file_mock.assert_called_with(raw_file, 'wb')
        _mock.write.assert_called()
        assert downloaded_files[0] == raw_file

    def test_bank_statements_transform_valid(self, file_mock, pdf_mock, tabula_mock, bank_statement_df_valid,
                                             config_valid, yahoo_config_valid,
                                             card_statements_valid):
        _mock = MagicMock()
        file_mock.return_value.__enter__.return_value = _mock
        card_expenses = BankStatementService(**yahoo_config_valid)
        tf_files = card_expenses.transform('file_test.pdf')
        paths = data_paths(DataRepo())
        assert tabula_mock.convert_into.call_args[0][1] == paths.tables_file('file_test.csv')
        assert tf_files['file_no_pass'] == paths.no_pass_file('file_test.pdf')
        assert tf_files['file_tables'] == paths.tables_file('file_test.csv')
        assert tf_files['file_data'] == paths.data_file('file_test_apr_2022.json')
        _mock.write.assert_called()
        df = pd.read_json(_mock.write.call_args[0][0].decode('utf-8'))
        # print(df.to_string())
        assert len(df) == 7
        print(df.query("date == '05-APR' and suma == '-5,2'").size)

    def test_bank_statements_transform_requested_valid(self, file_mock, pdf_mock, tabula_mock, bank_statement_df_valid,
                                                       config_valid, yahoo_config_valid,
                                                       card_statements_valid):
        _mock = MagicMock()
        file_mock.return_value.__enter__.return_value = _mock
        card_expenses = BankStatementService(**yahoo_config_valid)
        tf_files = card_expenses.transform('file_test.pdf')
        paths = data_paths(DataRepo())
        assert tabula_mock.convert_into.call_args[0][1] == paths.tables_file('file_test.csv')
        assert tf_files['file_no_pass'] == paths.no_pass_file('file_test.pdf')
        assert tf_files['file_tables'] == paths.tables_file('file_test.csv')
        assert tf_files['file_data'] == paths.data_file('file_test_apr_2022.json')
        _mock.write.assert_called()
        df = pd.read_json(_mock.write.call_args[0][0].decode('utf-8'))
        assert len(df) == 7

    def test_bank_statements_transform_entries_no_start_points_desc_and_date_on_first_column(self, file_mock, pdf_mock,
                                                                                             tabula_mock,
                                                                                             bank_statement_df_valid,
                                                                                             config_valid,
                                                                                             yahoo_config_valid,
                                                                                             card_statements_valid):
        test_file = 'file_test.pdf'
        df = self.transform(file_mock, test_file, yahoo_config_valid)
        print(df.to_string())
        assert len(df.query("date == '2022-04-05' and suma == -5.2 and desc.str.contains('APPLE')")) == 1

    def test_bank_statements_transform_entries_local_date_is_converted_to_standard_date(self, file_mock, pdf_mock,
                                                                                        tabula_mock,
                                                                                        bank_statement_local_date,
                                                                                        config_valid,
                                                                                        yahoo_config_valid,
                                                                                        card_statements_valid):
        test_file = 'file_test.pdf'
        df = self.transform(file_mock, test_file, yahoo_config_valid)
        print(df.to_string())
        assert len(df.query("date == '2022-01-01' and desc.str.contains('desc')")) == 1
        assert len(df.query("date == '2022-05-01' and desc.str.contains('desc')")) == 1
        assert len(df.query("date == '2022-06-01' and desc.str.contains('desc')")) == 1
        assert len(df.query("date == '2022-07-01' and desc.str.contains('desc')")) == 1
        assert len(df.query("date == '2022-11-01' and desc.str.contains('desc')")) == 1

    def test_bank_statements_transform_entries_other_transactions_entries(self, file_mock, pdf_mock,
                                                                          tabula_mock,
                                                                          bank_statement_df_valid,
                                                                          config_valid,
                                                                          yahoo_config_valid,
                                                                          card_statements_valid):
        test_file = 'file_test.pdf'
        df = self.transform(file_mock, test_file, yahoo_config_valid)
        print(df.to_string())
        assert len(df) == 7

        assert len(df.query(
            "date == '2022-04-21' and suma == -2.0 and desc.str.contains('Comision-Plata catre JOHN DOE')")) == 1
        assert len(df.query(
            "date == '2022-04-16' and suma == -1.0 and desc.str.contains('Taxa Serviciu SMS ZK78251578')")) == 1

    def test_bank_statements_transform_entries_space_between_description_entries(self, file_mock, pdf_mock,
                                                                                 tabula_mock,
                                                                                 bank_statement_df_valid,
                                                                                 config_valid,
                                                                                 yahoo_config_valid,
                                                                                 card_statements_valid):
        test_file = 'file_test.pdf'
        df = self.transform(file_mock, test_file, yahoo_config_valid)
        assert len(df.query(
            "date == '2022-04-07' "
            "and suma == -10.0 "
            "and desc.str.contains('Glovo 04APR CJSSW1FH1 BUCURESTI RO; 04-APR 09:27 +0,37 Puncte Star', regex=False)")) == 1

    def test_bank_statements_transform_sum_with_other_text_on_second_column(self, file_mock, pdf_mock,
                                                                            tabula_mock,
                                                                            bank_statement_df_valid,
                                                                            config_valid,
                                                                            yahoo_config_valid,
                                                                            card_statements_valid):
        test_file = 'file_test.pdf'
        df = self.transform(file_mock, test_file, yahoo_config_valid)
        # print(df.to_string())
        assert len(df) == 7

        assert len(df.query(
            "date == '2022-04-27' and suma == -2.01 and desc.str.contains('RON/XXX')")) == 1

    def test_bank_statements_transform_missing_statements(self, file_mock, pdf_mock,
                                                          tabula_mock,
                                                          bank_statement_missing_statements,
                                                          config_valid,
                                                          yahoo_config_valid,
                                                          card_statements_valid):
        test_file = 'file_test.pdf'
        df = self.transform(file_mock, test_file, yahoo_config_valid)
        # print(df.to_string())
        assert len(df) == 6

    def test_bank_statements_transform_entries_star_points_desc_and_date_on_first_column(self, file_mock, pdf_mock,
                                                                                         tabula_mock,
                                                                                         bank_statement_df_valid,
                                                                                         config_valid,
                                                                                         yahoo_config_valid,
                                                                                         card_statements_valid):
        test_file = 'file_test.pdf'
        df = self.transform(file_mock, test_file, yahoo_config_valid)
        assert len(df.query("date == '2022-04-07' and suma == -10 and desc.str.contains('Glovo')")) == 1

    def test_bank_statements_transform_entries_no_star_points_desc_and_date_on_first_and_second_column(self, file_mock,
                                                                                                       pdf_mock,
                                                                                                       tabula_mock,
                                                                                                       bank_statement_df_valid,
                                                                                                       config_valid,
                                                                                                       yahoo_config_valid,
                                                                                                       card_statements_valid):
        test_file = 'file_test.pdf'
        df = self.transform(file_mock, test_file, yahoo_config_valid)
        assert len(df.query("date == '2022-04-11' and suma == -11.0 and desc.str.contains('Glovo')")) == 1

    def test_bank_statements_transform_entries_star_points_desc_and_date_on_first_and_second_column(self, file_mock,
                                                                                                    pdf_mock,
                                                                                                    tabula_mock,
                                                                                                    bank_statement_df_valid,
                                                                                                    config_valid,
                                                                                                    yahoo_config_valid,
                                                                                                    card_statements_valid):
        test_file = 'file_test.pdf'
        df = self.transform(file_mock, test_file, yahoo_config_valid)
        assert len(df.query("date == '2022-04-11' and suma == -15 and desc.str.contains('ORANGE')")) == 1

    def transform(self, file_mock, test_file, yahoo_config_valid):
        _mock = MagicMock()
        file_mock.return_value.__enter__.return_value = _mock
        card_expenses = BankStatementService(**yahoo_config_valid)
        card_expenses.transform(test_file)
        _mock.write.assert_called()
        df = pd.read_json(_mock.write.call_args[0][0].decode('utf-8'))
        return df
