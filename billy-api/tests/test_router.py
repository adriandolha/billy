from datetime import datetime

from billy_api import bank_statements
from billy_api.bank_statements import BankStatementApi
import app


class TestRouter:
    def test_router_missing_path(self, config_valid, user_valid):
        event = {'queryStringParameters': {'query': 'glovo'},
                 'requestContext': {'httpMethod': 'GET'},
                 'headers': {'Authorization': ''},
                 'path': '/billy/not_found'
                 }
        result = app.lambda_handler(event, [])

        assert result['statusCode'] == 404
