from jobs_conftest import *
import json

import app


class TestJobsApi:
    def test_job_get_all(self, config_valid, user_valid, auth_requests, job_service_mock, job_valid):
        job_service_mock.table.query.return_value = {'Items':[job_valid.to_dict()]}
        print(job_service_mock)
        auth_requests.get.return_value.content = json.dumps('bla')
        event = {'path': '/billy/jobs',
                 'requestContext': {'httpMethod': 'GET'},
                 'headers': {'Authorization': ''}}
        response = app.lambda_handler(event, [])
        assert response['statusCode'] == 200
        result = json.loads(response['body'])
        assert result['total'] == 1
        assert len(result['items']) == 1
        _job = result['items'][0]
        job_dict = job_valid.to_dict()
        assert _job['id'] == job_dict['id']
        assert _job['created_at'] == job_dict['created_at']
        assert _job['status'] == job_dict['status']
        assert _job['payload'] == job_dict['payload']


