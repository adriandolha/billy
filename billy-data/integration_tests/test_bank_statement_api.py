import json
import os
import pandas

os.environ['env'] = 'test'


class TestBankStatementAPI:
    def test_bank_statement_collect_generated(self, config_valid, yahoo_config_valid, collect_event_valid):
        import app
        from billy_data.repo import data_repo
        response = app.lambda_handler(collect_event_valid, [])
        assert response['statusCode'] == 200
        result = json.loads(response['body'])
        downloaded_files = result['downloaded_files']
        print(downloaded_files)
        assert len(downloaded_files) == 1
        assert all([data_repo.exists(file) for file in downloaded_files])

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
