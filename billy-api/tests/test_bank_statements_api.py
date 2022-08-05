import json
from datetime import datetime

from billy_api import bank_statements
from billy_api.bank_statements import BankStatementApi
import app


class TestBankStatementsApi:
    def test_bank_statement_data_path_contains_username(self, config_valid, user_valid, data_valid, data_mock, auth_requests):
        auth_requests.get.return_value.content = json.dumps('bla')
        event = {'path': '/billy/bank_statements/search',
                 'requestContext': {'httpMethod': 'GET'},
                 'queryStringParameters': {'query': 'glovo'},
                 'headers': {'Authorization': ''}}
        app.lambda_handler(event, [])
        assert data_mock.return_value.get.call_args_list[0].args[0] == 'adolha/bank_statements/data.json'

    def test_bank_statement_search_multiple_criteria(self, config_valid, data_valid):
        api = BankStatementApi()
        print(datetime.now())
        search_result = api.search('glovo test', offset=0, limit=2)
        assert search_result.columns == ['date', 'desc', 'suma', 'category']
        assert search_result.search_count == 1
        assert ['2022-04-22', 'Glovo test entr1', -1, 'food'] == search_result.items[0]

    def test_bank_statement_search_query_words_order_different_than_columns_order(self, config_valid, data_valid):
        api = BankStatementApi()
        print(datetime.now())
        search_result = api.search('test glovo', offset=0, limit=2)
        assert search_result.columns == ['date', 'desc', 'suma', 'category']
        assert search_result.search_count == 1
        assert ['2022-04-22', 'Glovo test entr1', -1, 'food'] == search_result.items[0]

    def test_bank_statement_search_multiple_criteria_non_alphanumeric_query(self, config_valid, data_valid):
        api = BankStatementApi()
        search_result = api.search('2022 04 21', offset=0, limit=2)
        assert search_result.columns == ['date', 'desc', 'suma', 'category']
        assert search_result.search_count == 1
        assert ['2022-04-21', 'Glovo entr1', -1, 'food'] == search_result.items[0]

    def test_bank_statement_search_empty_query(self, config_valid, data_valid):
        api = BankStatementApi()
        print(datetime.now())
        search_result = api.search('', offset=0, limit=2)
        assert search_result.search_count == 4
        search_result = api.search(' ', offset=0, limit=2)
        assert search_result.search_count == 4

    def test_bank_statement_search_sorted_by_date_descending(self, config_valid, data_valid):
        api = BankStatementApi()
        print(datetime.now())
        search_result = api.search('glovo', offset=0, limit=2)
        assert len(search_result.items) == 2
        assert search_result.items[0][0] == '2022-04-22'
        assert search_result.items[1][0] == '2022-04-21'

    def test_bank_statement_search_auth(self, config_valid, data_valid, user_valid, auth_requests):
        auth_requests.get.return_value.content = json.dumps('bla')
        event = {'path': '/billy/bank_statements/search',
                 'requestContext': {'httpMethod': 'GET'},
                 'queryStringParameters': {'query': 'glovo'},
                 'headers': {'Authorization': ''}}
        result = app.lambda_handler(event, [])
        assert result['statusCode'] == 200
