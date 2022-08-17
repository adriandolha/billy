import config
import json
import os
import app
from billy_data.repo import data_repo
from billy_data.job import job_service, Job, JobStatus
from billy_data.provider import bank_statement_provider_service
os.environ['env'] = 'test'


class TestBankStatementAPI:
    def test_bank_statement_collect(self, config_valid, yahoo_config_valid, collect_event_valid, job_valid):
        job_service.save(job_valid)
        response = app.lambda_handler(collect_event_valid, [])
        assert response['statusCode'] == 200
        result = json.loads(response['body'])
        downloaded_files = result['downloaded_files']
        print(downloaded_files)
        assert len(downloaded_files) == 1
        assert all([data_repo.exists(file) for file in downloaded_files])

    def test_bank_statement_collect_ddb_stream_trigger(self, config_valid, yahoo_config_valid, collect_event_valid, job_valid):
        job_service.save(job_valid)

    def test_job_get_all(self, config_valid, yahoo_config_valid, collect_event_valid, test_job_valid):
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

    def test_provider(self, config_valid, yahoo_config_valid, collect_event_valid, bank_statement_provider_valid):
        providers = bank_statement_provider_service.get_all()

        if bank_statement_provider_valid.yahoo_host and len(providers) == 0:
            bank_statement_provider_service.save(bank_statement_provider_valid)

        provider = bank_statement_provider_service.get_all()[0]
        assert provider.yahoo_host == bank_statement_provider_valid.yahoo_host
        assert provider.yahoo_user == bank_statement_provider_valid.yahoo_user
        assert provider.yahoo_password == bank_statement_provider_valid.yahoo_password
        assert provider.yahoo_port == bank_statement_provider_valid.yahoo_port
        assert provider.card_statement_pdf_password == bank_statement_provider_valid.card_statement_pdf_password
