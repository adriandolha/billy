from jobs_conftest import *
import json

import app


class TestJobsApi:
    def test_job_get_all(self, config_valid, user_valid, auth_requests, job_service_mock, job_valid):
        job_service_mock.table.query.return_value = {'Items': [job_valid.to_dict()]}
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

    def test_job_save(self, config_valid, verified_user_valid, auth_requests, job_service_mock, job_request_valid):
        auth_requests.get.return_value.content = json.dumps('bla')
        response = self.save_job(job_request_valid)
        result = json.loads(response['body'])
        assert response['statusCode'] == 200
        assert result['status'] == 'CREATED'
        assert result['created_at']
        assert result['completed_at'] is None

    def test_delete_job(self, config_valid, verified_user_valid, auth_requests, job_service_mock, job_request_valid):
        auth_requests.get.return_value.content = json.dumps('bla')
        response = self.save_job(job_request_valid)
        assert response['statusCode'] == 200
        result = json.loads(response['body'])

        event = {'path': f'/billy/jobs/{result["id"]}',
                 'requestContext': {'httpMethod': 'DELETE'},
                 'pathParameters': {'job_id': result["id"]},
                 'headers': {'Authorization': ''}}
        response = app.lambda_handler(event, [])
        assert response['statusCode'] == 204
        job_service_mock.table.delete_item.assert_called()

    def save_job(self, job_request_valid):
        event = {'path': '/billy/jobs',
                 'requestContext': {'httpMethod': 'POST'},
                 'headers': {'Authorization': ''},
                 'body': json.dumps(job_request_valid)}
        response = app.lambda_handler(event, [])
        return response
