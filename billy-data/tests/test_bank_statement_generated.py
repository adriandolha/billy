import os

import pandas as pd
from mock import MagicMock

from billy_data.bank_statements import BankStatementService, SearchCriteria, data_paths, BankStatementEntry

os.environ['env'] = 'test'


class TestBankStatementGenerated:
    def test_bank_statement_collect(self, temp_file_mock, config_valid, yahoo_config_valid,
                                    bank_statements_data_repo,
                                    bank_statements_mocks,
                                    card_statements_valid):
        _mock = MagicMock()
        temp_file_mock.return_value.__enter__.return_value = _mock
        card_expenses = BankStatementService(**yahoo_config_valid)
        downloaded_files = card_expenses.collect(
            SearchCriteria().subject(['Extras de cont Star Gold - Aprilie 2022']))
        raw_file = data_paths(bank_statements_data_repo).raw_file('bank_statement_100.pdf')
        assert bank_statements_data_repo.save.call_args[0][0] == raw_file
        assert len(downloaded_files) > 0

    def test_bank_statements_transform_valid(self, temp_file_mock, tabula_mock, bank_statement_df_valid,
                                             bank_statements_data_repo,
                                             bank_statements_mocks,
                                             yahoo_config_valid,
                                             card_statements_valid):
        _mock = MagicMock()
        temp_file_mock.return_value.__enter__.return_value = _mock
        _mock.name = 'file_test.pdf'
        card_expenses = BankStatementService(**yahoo_config_valid)
        tf_files = card_expenses.transform('file_test.pdf')
        paths = data_paths(bank_statements_data_repo)
        assert tabula_mock.convert_into.call_args[0][1] == 'file_test.pdf'
        assert tf_files['file_no_pass'] == paths.no_pass_file('file_test.pdf')
        assert tf_files['file_tables'] == paths.tables_file('file_test.csv')
        assert tf_files['file_data'] == paths.data_file('file_test_apr_2022.json')
        _mock.write.assert_called()
        data_json = bank_statements_data_repo.save.call_args[0][1].decode('utf-8')
        df = pd.read_json(data_json)
        # print(df.to_string())
        assert len(df) == 7
        print(df.query("date == '05-APR' and suma == '-5,2'").size)

    def test_bank_statements_transform_requested_valid(self, temp_file_mock, tabula_mock, bank_statement_df_valid,
                                                       bank_statements_data_repo,
                                                       bank_statements_mocks,
                                                       yahoo_config_valid,
                                                       card_statements_valid):
        _mock = MagicMock()
        temp_file_mock.return_value.__enter__.return_value = _mock
        _mock.name = 'file_test.pdf'
        card_expenses = BankStatementService(**yahoo_config_valid)
        tf_files = card_expenses.transform('file_test.pdf')
        paths = data_paths(bank_statements_data_repo)
        assert tabula_mock.convert_into.call_args[0][1] == 'file_test.pdf'
        assert tf_files['file_no_pass'] == paths.no_pass_file('file_test.pdf')
        assert tf_files['file_tables'] == paths.tables_file('file_test.csv')
        assert tf_files['file_data'] == paths.data_file('file_test_apr_2022.json')
        _mock.write.assert_called()
        data_json = bank_statements_data_repo.save.call_args[0][1].decode('utf-8')
        df = pd.read_json(data_json)
        assert len(df) == 7

    def test_bank_statements_transform_entries_no_start_points_desc_and_date_on_first_column(self, temp_file_mock,
                                                                                             bank_statements_data_repo,
                                                                                             bank_statement_df_valid,
                                                                                             bank_statements_mocks,
                                                                                             yahoo_config_valid,
                                                                                             card_statements_valid):
        test_file = 'file_test.pdf'
        df = self.transform(temp_file_mock, test_file, yahoo_config_valid, bank_statements_data_repo)
        print(df.to_string())
        assert len(df.query("date == '2022-04-05' and suma == -5.2 and desc.str.contains('APPLE')")) == 1

    def test_bank_statements_transform_entries_local_date_is_converted_to_standard_date(self, temp_file_mock,
                                                                                        bank_statements_mocks,
                                                                                        bank_statements_data_repo,
                                                                                        bank_statement_local_date,
                                                                                        yahoo_config_valid,
                                                                                        card_statements_valid):
        test_file = 'file_test.pdf'
        df = self.transform(temp_file_mock, test_file, yahoo_config_valid, bank_statements_data_repo)
        print(df.to_string())
        assert len(df.query("date == '2022-01-01' and desc.str.contains('desc')")) == 1
        assert len(df.query("date == '2022-05-01' and desc.str.contains('desc')")) == 1
        assert len(df.query("date == '2022-06-01' and desc.str.contains('desc')")) == 1
        assert len(df.query("date == '2022-07-01' and desc.str.contains('desc')")) == 1
        assert len(df.query("date == '2022-11-01' and desc.str.contains('desc')")) == 1

    def test_bank_statements_transform_entries_other_transactions_entries(self, temp_file_mock,
                                                                          bank_statements_mocks,
                                                                          bank_statements_data_repo,
                                                                          bank_statement_df_valid,
                                                                          config_valid,
                                                                          yahoo_config_valid,
                                                                          card_statements_valid):
        test_file = 'file_test.pdf'
        df = self.transform(temp_file_mock, test_file, yahoo_config_valid, bank_statements_data_repo)
        print(df.to_string())
        assert len(df) == 7

        assert len(df.query(
            "date == '2022-04-21' and suma == -2.0 and desc.str.contains('Comision-Plata catre JOHN DOE')")) == 1
        assert len(df.query(
            "date == '2022-04-16' and suma == -1.0 and desc.str.contains('Taxa Serviciu SMS ZK78251578')")) == 1

    def test_bank_statements_transform_entries_space_between_description_entries(self, temp_file_mock,
                                                                                 bank_statements_mocks,
                                                                                 bank_statements_data_repo,
                                                                                 bank_statement_df_valid,
                                                                                 config_valid,
                                                                                 yahoo_config_valid,
                                                                                 card_statements_valid):
        test_file = 'file_test.pdf'
        df = self.transform(temp_file_mock, test_file, yahoo_config_valid, bank_statements_data_repo)
        assert len(df.query(
            "date == '2022-04-07' "
            "and suma == -10.0 "
            "and desc.str.contains('Glovo 04APR CJSSW1FH1 BUCURESTI RO; 04-APR 09:27 +0,37 Puncte Star', regex=False)")) == 1

    def test_bank_statements_transform_sum_with_other_text_on_second_column(self, temp_file_mock,
                                                                            bank_statements_mocks,
                                                                            bank_statements_data_repo,
                                                                            bank_statement_df_valid,
                                                                            config_valid,
                                                                            yahoo_config_valid,
                                                                            card_statements_valid):
        test_file = 'file_test.pdf'
        df = self.transform(temp_file_mock, test_file, yahoo_config_valid, bank_statements_data_repo)
        # print(df.to_string())
        assert len(df) == 7

        assert len(df.query(
            "date == '2022-04-27' and suma == -2.01 and desc.str.contains('RON/XXX')")) == 1

    def test_bank_statements_transform_missing_statements(self, temp_file_mock,
                                                          bank_statements_mocks,
                                                          bank_statements_data_repo,
                                                          bank_statement_missing_statements,
                                                          config_valid,
                                                          yahoo_config_valid,
                                                          card_statements_valid):
        test_file = 'file_test.pdf'
        df = self.transform(temp_file_mock, test_file, yahoo_config_valid, bank_statements_data_repo)
        # print(df.to_string())
        assert len(df) == 6

    def test_bank_statements_transform_entries_star_points_desc_and_date_on_first_column(self, temp_file_mock,
                                                                                         bank_statements_mocks,
                                                                                         bank_statements_data_repo,
                                                                                         bank_statement_df_valid,
                                                                                         config_valid,
                                                                                         yahoo_config_valid,
                                                                                         card_statements_valid):
        test_file = 'file_test.pdf'
        df = self.transform(temp_file_mock, test_file, yahoo_config_valid, bank_statements_data_repo)
        assert len(df.query("date == '2022-04-07' and suma == -10 and desc.str.contains('Glovo')")) == 1

    def test_bank_statements_transform_entries_no_star_points_desc_and_date_on_first_and_second_column(self,
                                                                                                       temp_file_mock,
                                                                                                       bank_statements_mocks,
                                                                                                       bank_statements_data_repo,
                                                                                                       bank_statement_df_valid,
                                                                                                       config_valid,
                                                                                                       yahoo_config_valid,
                                                                                                       card_statements_valid):
        test_file = 'file_test.pdf'
        df = self.transform(temp_file_mock, test_file, yahoo_config_valid, bank_statements_data_repo)
        assert len(df.query("date == '2022-04-11' and suma == -11.0 and desc.str.contains('Glovo')")) == 1

    def test_bank_statements_transform_entries_star_points_desc_and_date_on_first_and_second_column(self,
                                                                                                    temp_file_mock,
                                                                                                    bank_statements_mocks,
                                                                                                    bank_statements_data_repo,
                                                                                                    bank_statement_df_valid,
                                                                                                    config_valid,
                                                                                                    yahoo_config_valid,
                                                                                                    card_statements_valid):
        test_file = 'file_test.pdf'
        df = self.transform(temp_file_mock, test_file, yahoo_config_valid, bank_statements_data_repo)
        assert len(df.query("date == '2022-04-11' and suma == -15 and desc.str.contains('ORANGE')")) == 1

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
