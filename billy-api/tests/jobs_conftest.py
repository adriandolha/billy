import json
from datetime import datetime

import pytest
from mock import mock

from billy_api.category import CategoryService
from billy_api.job import JobService, Job, JobStatus


@pytest.fixture()
def job_valid():
    return Job(id='test_job_1',
               created_at=datetime.now(),
               status=JobStatus.CREATED,
               payload=json.dumps({'op': 'test'})
               )


@pytest.fixture()
def job_table_mock():
    with mock.patch('billy_api.job.boto3') as boto_mock:
        with mock.patch('billy_api.job.Key') as _Key:
            yield boto_mock


@pytest.fixture()
def job_service_mock(job_table_mock):
    _service = JobService()
    with mock.patch('billy_api.routes.jobs.job_service', _service) as job_service:
        # job_service.return_value = _service
        yield _service


