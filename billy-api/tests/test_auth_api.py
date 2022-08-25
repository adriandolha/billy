import json
from datetime import datetime

from billy_api import bank_statements
from billy_api.auth import Groups, User
from billy_api.bank_statements import BankStatementApi
import app


class TestAuthApi:
    def test_initiate_auth(self, config_valid, user_valid):
        event = {'queryStringParameters': {'query': 'glovo'},
                 'headers': {'Authorization': ''},
                 'requestContext': {'httpMethod': 'GET'},
                 'path': '/billy/auth/sign_in/cognito'}
        result = app.lambda_handler(event, [])
        assert result['statusCode'] == 302
        assert 'amazoncognito' in result['headers']['Location']

    def test_get_token(self, config_valid, user_valid, auth_requests, jwk_mock, auth_service_mock):
        event = {'queryStringParameters': {'code': '123545'},
                 'requestContext': {'httpMethod': 'GET'},
                 'headers': {'Authorization': ''},
                 'path': '/billy/auth/token/cognito'}
        auth_requests.post.return_value.status_code = 200
        auth_service_mock.get_user.return_value = User('test', Groups.USERS.value)
        auth_requests.post.return_value.content = json.dumps({'id_token': 'id_token'}).encode('utf-8')

        result = app.lambda_handler(event, [])
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body.get('id_token')
        assert body.get('user')
        assert body.get('user')['username'] == 'test'

    def test_get_token_add_user(self, config_valid, user_valid, auth_requests, jwk_mock, auth_service_mock):
        event = {'queryStringParameters': {'code': '123545'},
                 'requestContext': {'httpMethod': 'GET'},
                 'headers': {'Authorization': ''},
                 'path': '/billy/auth/token/cognito'}
        auth_requests.post.return_value.status_code = 200
        auth_service_mock.get_user.return_value = None
        auth_service_mock.add_user.return_value = User('test', Groups.USERS.value)
        auth_requests.post.return_value.content = json.dumps({'id_token': 'id_token'}).encode('utf-8')

        result = app.lambda_handler(event, [])
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body.get('id_token')
        assert body.get('user')
        assert body.get('user')['username'] == 'test'

    def test_cors(self, config_valid, user_valid, auth_requests, jwk_mock, auth_service_mock):
        event = {'queryStringParameters': {'code': '123545'},
                 'requestContext': {'httpMethod': 'GET'},
                 'headers': {'Authorization': ''},
                 'path': '/billy/auth/token/cognito'}
        auth_requests.post.return_value.status_code = 200
        auth_service_mock.get_user.return_value = User('test', Groups.USERS.value)
        auth_requests.post.return_value.content = json.dumps({'id_token': 'id_token'}).encode('utf-8')

        result = app.lambda_handler(event, [])
        assert result['statusCode'] == 200
        assert result['headers']['Access-Control-Allow-Origin'] == '*'

    def test_preflight_allowed(self, config_valid, user_valid, auth_requests):
        event = {'queryStringParameters': {'code': '123545'},
                 'requestContext': {'httpMethod': 'OPTIONS'},
                 'headers': {'Authorization': ''},
                 'path': '/billy/auth/token/cognito'}
        # auth_requests.post.return_value.status_code = 200
        # auth_requests.post.return_value.content = json.dumps('bla').encode('utf-8')

        result = app.lambda_handler(event, [])
        assert result['statusCode'] == 200
        assert result['body'] == json.dumps('ok')
        assert result['headers']['Access-Control-Allow-Origin'] == '*'
