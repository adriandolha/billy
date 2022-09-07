import json
import requests


# Bank statements integration tests

class TestBankStatementsApi:
    def test_bank_statement_search_valid(self, config_valid, id_token, api_url):
        response = requests.get(f'{api_url}/bank_statements/search?query=glovo&offset=0&limit=10', headers={
            'Authorization': id_token
        })
        assert response.status_code == 200
        search_result = json.loads(response.content)
        assert search_result['total'] > 0
        assert len(search_result['items']) > 0

    def test_bank_statement_upload_url_valid(self, config_valid, id_token, api_url):
        response = requests.get(f'{api_url}/bank_statements/upload_url', headers={
            'Authorization': id_token
        })
        assert response.status_code == 200
        result = json.loads(response.content)
        print(result)
        assert 'https://' in result['upload_url']

    def test_bank_statement_search_auth(self, config_valid, id_token, api_url):
        response = requests.get(f'{api_url}/bank_statements/search?query=glovo&offset=0&limit=10')
        assert response.status_code == 401

    def test_bank_statement_upload_url_auth(self, config_valid, id_token, api_url):
        response = requests.get(f'{api_url}/bank_statements/upload_url')
        assert response.status_code == 401
