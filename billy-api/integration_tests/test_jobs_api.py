import json
import requests


class TestIntegrationJobsApi:
    def test_job_get_all(self, config_valid, id_token, api_url):
        response = requests.get(f'{api_url}/jobs', headers={
            'Authorization': id_token
        })
        assert response.status_code == 200
        result = json.loads(response.content)
        assert len(result['items']) > 0
        assert result['total'] > 1

    def test_jobs_auth(self, config_valid, id_token, api_url):
        response = requests.get(f'{api_url}/jobs')
        assert response.status_code == 401
