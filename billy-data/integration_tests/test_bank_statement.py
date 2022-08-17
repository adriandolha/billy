import os

import pandas

from billy_data.bank_statements import BankStatementService, SearchCriteria
from os import listdir
from os.path import isfile, join

os.environ['env'] = 'test'


class TestBankStatement:
    def ds_files(self, ds_path):
        return [f for f in listdir(ds_path) if isfile(join(ds_path, f))]

    def test_bank_statement_collect_generated(self, config_valid, yahoo_config_valid):
        search_criteria = SearchCriteria()
        search_criterias = ' '.join([search_criteria.subject(['Extras de cont Star Gold - Februarie 2022']),
                                     search_criteria.since('11-Jul-2021')])
        downloaded_files = BankStatementService(**yahoo_config_valid).collect(
            search_criterias)
        assert len(downloaded_files) == 1
        assert all([os.path.exists(file) for file in downloaded_files])

    def test_bank_statement_load(self, config_valid, yahoo_config_valid):
        result = BankStatementService(**yahoo_config_valid).load()
        print(result)
        assert result['data_file']
        assert result['df_no'] > 0

    def test_bank_statement_transform_generated(self, yahoo_config_valid, config_valid):
        downloaded_files = BankStatementService(**yahoo_config_valid).collect(
            SearchCriteria().subject(['Extras de cont Star Gold - Aprilie 2022']))
        assert len(downloaded_files) == 1
        card_expenses = BankStatementService(**yahoo_config_valid)
        tf_files = card_expenses.transform(downloaded_files[0])
        assert os.path.exists(tf_files['file_no_pass'])
        assert os.path.exists(tf_files['file_tables'])
        assert os.path.exists(tf_files['file_data'])
        df = pandas.read_json(tf_files['file_data'])
        print(df.to_string())
        assert len(df) == 88
        assert df['suma'].sum() == -9325.0

    def test_bank_statement_transform_generated_star_forte(self, yahoo_config_valid, config_valid):
        downloaded_files = BankStatementService(**yahoo_config_valid).collect(
            SearchCriteria().subject(['Extras de cont Star Forte - Iulie 2019, DOLHA ADRIAN']))
        assert len(downloaded_files) == 1
        card_expenses = BankStatementService(**yahoo_config_valid)
        tf_files = card_expenses.transform(downloaded_files[0])
        assert os.path.exists(tf_files['file_no_pass'])
        assert os.path.exists(tf_files['file_tables'])
        assert os.path.exists(tf_files['file_data'])
        df = pandas.read_json(tf_files['file_data'])
        assert len(df) == 22
        assert df['suma'].sum() == 4841.52

    def test_bank_statements_transform_requested(self, yahoo_config_valid, config_valid):
        search_criteria = SearchCriteria()
        search_criterias = ' '.join(
            [search_criteria.subject(['Extras de cont Banca Transilvania solicitat prin aplicatia mobile banking']),
             search_criteria.on_date('11-Jul-2022')])
        downloaded_files = BankStatementService(**yahoo_config_valid).collect(search_criterias)
        assert len(downloaded_files) == 1
        card_expenses = BankStatementService(**yahoo_config_valid)
        tf_files = card_expenses.transform(downloaded_files[0])
        assert os.path.exists(tf_files['file_no_pass'])
        assert os.path.exists(tf_files['file_tables'])
        assert os.path.exists(tf_files['file_data'])
        df = pandas.read_json(tf_files['file_data'])
        print(df.to_string())
        assert len(df) == 9
        assert df['suma'].sum() == -1721.3300000000017

    # def test_bank_statement_transform_generated_star_forte(self, yahoo_config_valid, config_valid):
    #     paths = data_paths(DataRepo())
    #     card_expenses = BankStatementService(**yahoo_config_valid)
    #     tf_files = card_expenses.transform(paths.raw_file('bank_statement_864.pdf'))
    #     assert os.path.exists(tf_files['file_no_pass'])
    #     assert os.path.exists(tf_files['file_tables'])
    #     assert os.path.exists(tf_files['file_data'])
    #     df = pandas.read_json(tf_files['file_data'])
    #     assert len(df) == 22
    #     assert df['suma'].sum() == 4841.52
