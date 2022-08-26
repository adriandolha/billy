from categories_conftest import *
import json

import app


class TestCategoriesApi:
    def test_category_save(self, config_valid, verified_user_valid, auth_requests, category_service_mock,
                           category_request_valid):
        auth_requests.get.return_value.content = json.dumps('bla')
        # category_service_mock
        response = self.save_category(category_request_valid)
        assert response['statusCode'] == 200
        result = json.loads(response['body'])
        print(result)
        assert result['name'] == result['name']
        assert result['key_words'] == result['key_words']

    def test_category_update(self, config_valid, verified_user_valid, auth_requests, category_service_mock,
                             category_request_valid):
        auth_requests.get.return_value.content = json.dumps('bla')
        event = {'path': f'/billy/categories/{category_request_valid["name"]}',
                 'requestContext': {'httpMethod': 'PUT'},
                 'pathParameters': {'category_name': category_request_valid["name"]},
                 'headers': {'Authorization': ''},
                 'body': json.dumps(category_request_valid)}
        response = app.lambda_handler(event, [])
        assert response['statusCode'] == 200
        result = json.loads(response['body'])
        print(result)
        assert result['name'] == result['name']
        assert result['key_words'] == result['key_words']

    def save_category(self, category_request_valid):
        event = {'path': '/billy/categories',
                 'requestContext': {'httpMethod': 'POST'},
                 'headers': {'Authorization': ''},
                 'body': json.dumps(category_request_valid)}
        response = app.lambda_handler(event, [])
        return response

    def test_delete_category(self, config_valid, verified_user_valid, auth_requests, category_service_mock,
                             category_request_valid):
        auth_requests.get.return_value.content = json.dumps('bla')
        response = self.save_category(category_request_valid)
        assert response['statusCode'] == 200
        result = json.loads(response['body'])

        event = {'path': f'/billy/categories/{result["name"]}',
                 'requestContext': {'httpMethod': 'DELETE'},
                 'pathParameters': {'category_name': result["name"]},
                 'headers': {'Authorization': ''}}
        response = app.lambda_handler(event, [])
        assert response['statusCode'] == 204
        category_service_mock.table.delete_item.assert_called()
