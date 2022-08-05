import json
import requests


class TestBankStatementsApi:
    def test_bank_statement_search_valid(self, config_valid, id_token, api_url):
        response = requests.get(f'{api_url}/bank_statements/search?query=glovo&offset=0&limit=10', headers={
            'Authorization': id_token
        })
        assert response.status_code == 200
        search_result = json.loads(response.content)
        assert search_result['total'] > 0
        assert len(search_result['items']) > 0

    def test_bank_statement_search_auth(self, config_valid, id_token, api_url):
        response = requests.get(f'{api_url}/bank_statements/search?query=glovo&offset=0&limit=10')
        assert response.status_code == 401
