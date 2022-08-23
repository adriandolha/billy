import uuid
from datetime import datetime

import config
import json
import os
import app
from billy_data.repo import data_repo
from billy_data.job import job_service, Job, JobStatus
from billy_data.provider import bank_statement_provider_service
from billy_data.events_consumers import transform, load
from billy_data.events import publish, Event
import time

os.environ['env'] = 'test'


def wait_until(condition, timeout, period, *args, **kwargs):
    mustend = time.time() + timeout
    while time.time() < mustend:
        if condition(*args, **kwargs):
            return True
        time.sleep(period)
    return False


class TestBankStatementAPI:
    def test_bank_statement_collect(self, config_valid, yahoo_config_valid, process_event_valid, job_valid):
        job_service.save(job_valid)
        response = app.lambda_handler(process_event_valid, [])
        assert response['statusCode'] == 200
        result = json.loads(response['body'])
        downloaded_files = result['collect']['downloaded_files']
        print(downloaded_files)
        assert len(downloaded_files) == 1
        assert all([data_repo.exists(file) for file in downloaded_files])

    def test_bank_statement_transform(self, config_valid, yahoo_config_valid, process_event_valid,
                                      transform_event_valid):
        result = transform(transform_event_valid)
        tf_results = result['transform']
        print(tf_results)
        assert len(tf_results) > 0
        assert tf_results[0][transform_event_valid['files'][0]]['status'] == 'success'
        data_file = tf_results[0][transform_event_valid['files'][0]]['result']['file_data']
        assert data_file == f'{config_valid["cognito_user"]}/bank_statements/data/bank_statement_4724_feb_2022.json'

    def test_bank_statement_load(self, config_valid, yahoo_config_valid, process_event_valid,
                                 load_event_valid):
        result = load(load_event_valid)
        load_results = result['load']
        print(load_results)
        assert len(load_results) > 0
        assert load_results[0]['status'] == 'success'
        _result = load_results[0]['result']
        data_file = _result['data_file']
        assert data_file == f'{config_valid["cognito_user"]}/bank_statements/data.json'
        assert _result['df_no'] == 1
        assert _result['total_bank_statements_entries'] == 76

    def test_bank_statement_process_ddb_stream_trigger(self, config_valid, yahoo_config_valid, process_event_valid,
                                                       job_valid):
        job_service.save(job_valid)

        def is_job_completed(job_id):
            job = job_service.get(job_id)
            return job and job.status == JobStatus.COMPLETED

        assert wait_until(is_job_completed, timeout=30, period=0.5, job_id=job_valid.id)

    def test_bank_statement_load_all_ddb_stream_trigger(self, config_valid, yahoo_config_valid, process_event_valid):
        all_data_files = data_repo.list_files(f'{config_valid["cognito_user"]}/bank_statements/data/')
        print(all_data_files)

        job = Job(id=str(uuid.uuid4()),
                  created_at=datetime.now(),
                  status=JobStatus.CREATED,
                  payload=json.dumps({'op': 'load',
                                      'username': config_valid['cognito_user'], 'files': ['ALL']}
                                     )
                  )
        job_service.save(job)

        def is_job_completed(job_id):
            job = job_service.get(job_id)
            return job and job.status == JobStatus.COMPLETED

        assert wait_until(is_job_completed, timeout=30, period=0.5, job_id=job.id)

    def test_job_get_all(self, config_valid, yahoo_config_valid, process_event_valid, test_job_valid):
        job_service.save(test_job_valid)
        jobs = job_service.get_all()
        print(jobs)
        assert len(jobs) > 1
        _job = None
        for job in jobs:
            if job.id == test_job_valid.id:
                _job = job
        assert _job
        assert _job.status == JobStatus.CREATED
        assert _job.id == test_job_valid.id
        assert _job.payload == test_job_valid.payload

    def test_job_update(self, config_valid, yahoo_config_valid, process_event_valid, test_job_valid):
        job = Job(id=str(uuid.uuid4()),
                  created_at=datetime.now(),
                  status=JobStatus.CREATED,
                  payload=json.dumps({'op': 'test'})
                  )
        job_service.save(job)
        job = job_service.get(job.id)
        assert job.status == JobStatus.CREATED
        job.status = JobStatus.COMPLETED
        job_service.save(job)
        job = job_service.get(job.id)
        assert job.status == JobStatus.COMPLETED

    def test_sns_publish(self, config_valid, yahoo_config_valid, process_event_valid, test_job_valid):
        job = Job(id=str(uuid.uuid4()),
                  created_at=datetime.now(),
                  status=JobStatus.CREATED,
                  payload=json.dumps({'op': 'process',
                                      'username': config_valid['cognito_user'],
                                      'search_criteria':
                                          {
                                              'subjects':
                                                  [
                                                      'Extras de cont Star Gold - Februarie 2022'
                                                  ],
                                              'since': '11-Jul-2021'
                                          }
                                      })
                  )
        # response = publish(Event(name='test.event', payload=job.to_json()))
        response = publish(Event(name='job.created', payload=job.to_json()))
        assert response.get('MessageId')

    def test_provider(self, config_valid, yahoo_config_valid, process_event_valid, bank_statement_provider_valid):
        providers = bank_statement_provider_service.get_all()

        if bank_statement_provider_valid.yahoo_host and len(providers) == 0:
            bank_statement_provider_service.save(bank_statement_provider_valid)

        provider = bank_statement_provider_service.get_all()[0]
        assert provider.yahoo_host == bank_statement_provider_valid.yahoo_host
        assert provider.yahoo_user == bank_statement_provider_valid.yahoo_user
        assert provider.yahoo_password == bank_statement_provider_valid.yahoo_password
        assert provider.yahoo_port == bank_statement_provider_valid.yahoo_port
        assert provider.card_statement_pdf_password == bank_statement_provider_valid.card_statement_pdf_password
