import json
from datetime import datetime

from billy_api import bank_statements
from billy_api.bank_statements import BankStatementApi
import app


class TestDashboardApi:
    def test_bank_stats_expenses_per_month_and_category(self, config_valid, user_valid, auth_requests, stats_valid):
        auth_requests.get.return_value.content = json.dumps('bla')
        event = {'path': '/billy/stats/expenses_per_month_and_category',
                 'requestContext': {'httpMethod': 'GET'},
                 'queryStringParameters': {'query': 'glovo'},
                 'headers': {'Authorization': ''}}
        response = app.lambda_handler(event, [])
        assert response['statusCode'] == 200
        result = json.loads(response['body'])
        assert result['columns'] == ['category', 'year', 'month', 'suma']
        assert ['food', 2022, 4, 4] in result['items']
        assert ['phone', 2022, 6, 2] in result['items']

    def test_bank_stats_expenses_per_month_and_category_round_and_abs(self, config_valid, user_valid, auth_requests,
                                                                      stats_valid):
        auth_requests.get.return_value.content = json.dumps('bla')
        event = {'path': '/billy/stats/expenses_per_month_and_category',
                 'requestContext': {'httpMethod': 'GET'},
                 'queryStringParameters': {'query': 'glovo'},
                 'headers': {'Authorization': ''}}
        response = app.lambda_handler(event, [])
        assert response['statusCode'] == 200
        result = json.loads(response['body'])
        assert result['columns'] == ['category', 'year', 'month', 'suma']
        assert ['gas', 2022, 6, 1] in result['items']

    def test_bank_stats_expenses_per_month(self, config_valid, user_valid, auth_requests, stats_valid):
        auth_requests.get.return_value.content = json.dumps('bla')
        event = {'path': '/billy/stats/expenses_per_month',
                 'requestContext': {'httpMethod': 'GET'},
                 'queryStringParameters': {'query': 'glovo'},
                 'headers': {'Authorization': ''}}
        response = app.lambda_handler(event, [])
        assert response['statusCode'] == 200
        result = json.loads(response['body'])
        assert result['columns'] == ['year', 'month', 'suma']
        assert [2022, 4, 4] in result['items']
        assert [2022, 6, 4] in result['items']
