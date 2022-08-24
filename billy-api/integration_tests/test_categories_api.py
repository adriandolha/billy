import json
import requests


class TestIntegrationCategoriesApi:
    def test_category_get_all(self, config_valid, id_token, api_url):
        response = requests.get(f'{api_url}/categories', headers={
            'Authorization': id_token
        })
        assert response.status_code == 200
        result = json.loads(response.content)
        assert len(result['items']) > 0
        assert result['total'] > 1

    def test_category_auth(self, config_valid, id_token, api_url):
        response = requests.get(f'{api_url}/categories')
        assert response.status_code == 401
