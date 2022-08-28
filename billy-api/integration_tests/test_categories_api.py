import json
import requests

from billy_api.app_context import app_context
from billy_api.category import CategoryService


class TestIntegrationCategoriesApi:
    def test_category_get_all(self, config_valid, id_token, api_url):
        response = requests.get(f'{api_url}/categories', headers={
            'Authorization': id_token
        })
        assert response.status_code == 200
        result = json.loads(response.content)
        assert len(result['items']) > 0
        assert result['total'] > 1

    def test_category_save(self, config_valid, id_token, api_url):
        category = {'name': 'test_category',
                    'key_words': ['hard_to_match_key_word1']}
        category_updated = {'name': 'test_category',
                            'key_words': ['hard_to_match_key_updated_word1', 'hard_to_match_key_updated_word2']}
        response = self.save_category(api_url, category, id_token)
        assert response.status_code == 200
        result = json.loads(response.content)
        print(result)
        assert result['name'] == 'test_category'
        assert 'hard_to_match_key_word1' in result['key_words']

        response = self.save_category(api_url, category_updated, id_token)
        assert response.status_code == 200
        result = json.loads(response.content)
        print(result)
        assert result['name'] == 'test_category'
        assert category_updated['key_words'] == result['key_words']

    def test_category_update(self, config_valid, id_token, api_url):
        category = {'name': 'test_category',
                    'key_words': ['hard_to_match_key_word1']}
        category_updated = {'name': 'test_category',
                            'key_words': ['hard_to_match_key_updated_word1', 'hard_to_match_key_updated_word2']}
        response = self.save_category(api_url, category, id_token)
        assert response.status_code == 200
        result = json.loads(response.content)
        print(result)
        assert result['name'] == 'test_category'
        assert 'hard_to_match_key_word1' in result['key_words']

        response = requests.put(f'{api_url}/categories/{result["name"]}',
                                headers={
                                    'Authorization': id_token
                                },
                                json=category_updated)

        assert response.status_code == 200
        result = json.loads(response.content)
        print(result)
        assert result['name'] == 'test_category'
        assert category_updated['key_words'] == result['key_words']

    def test_category_delete(self, config_valid, id_token, api_url):
        category = {'name': 'test_category_delete',
                    'key_words': ['hard_to_match_key_word1']}
        response = self.save_category(api_url, category, id_token)
        assert response.status_code == 200
        result = json.loads(response.content)
        print(result)
        response = requests.delete(f'{api_url}/categories/{category["name"]}', headers={
            'Authorization': id_token
        })
        assert response.status_code == 204

    def save_category(self, api_url, category, id_token):
        response = requests.post(f'{api_url}/categories',
                                 headers={
                                     'Authorization': id_token
                                 },
                                 json=category)
        return response

    def test_category_auth(self, config_valid, id_token, api_url):
        response = requests.get(f'{api_url}/categories')
        assert response.status_code == 401
