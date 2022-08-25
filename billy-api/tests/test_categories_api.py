from categories_conftest import *
import json

import app


class TestCategoriesApi:
    def test_category_save(self, config_valid, verified_user_valid, auth_requests, category_service_mock,
                           category_request_valid):
        auth_requests.get.return_value.content = json.dumps('bla')
        # category_service_mock
        event = {'path': '/billy/categories',
                 'requestContext': {'httpMethod': 'POST'},
                 'headers': {'Authorization': ''},
                 'body': json.dumps(category_request_valid)}
        response = app.lambda_handler(event, [])
        assert response['statusCode'] == 200
        result = json.loads(response['body'])
        print(result)
        assert result['name'] == result['name']
        assert result['key_words'] == result['key_words']
