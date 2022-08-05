import json
import requests


class TestBankStatementsApi:
    def test_stats_expenses_per_month(self, config_valid, id_token, api_url):
        response = requests.get(f'{api_url}/stats/expenses_per_month', headers={
            'Authorization': id_token
        })
        assert response.status_code == 200
        result = json.loads(response.content)
        assert len(result['items']) > 0
        assert result['columns'] == ['year', 'month', 'suma']

    def test_stats_expenses_per_month_auth(self, config_valid, id_token, api_url):
        response = requests.get(f'{api_url}/stats/expenses_per_month')
        assert response.status_code == 401

    def test_stats_expenses_per_month_and_category(self, config_valid, id_token, api_url):
        response = requests.get(f'{api_url}/stats/expenses_per_month_and_category', headers={
            'Authorization': id_token
        })
        assert response.status_code == 200
        result = json.loads(response.content)
        assert len(result['items']) > 0
        assert result['columns'] == ['category', 'year', 'month', 'suma']

    def test_stats_expenses_per_month_and_category_auth(self, config_valid, id_token, api_url):
        response = requests.get(f'{api_url}/stats/expenses_per_month_and_category')
        assert response.status_code == 401
