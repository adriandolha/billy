import json
import os
import app
from billy_data.job import JobStatus
from events_conftest import *


class TestJob:
    def test_data_stream_job_created(self, file_mock, config_valid, yahoo_config_valid, card_statements_valid,
                                     ddb_job_created_valid, events_sns_topic):
        app.lambda_handler(ddb_job_created_valid, [])
        sns_publish_args = events_sns_topic.publish.call_args[1]
        print(sns_publish_args)
        assert sns_publish_args['MessageStructure'] == 'json'
        assert sns_publish_args['MessageAttributes']['event_name']['StringValue'] == 'job.created'
        assert sns_publish_args['Subject'] == 'application event'
        job = json.loads(json.loads(sns_publish_args['Message'])['default'])
        assert job['id'] == ddb_job_created_valid['Records'][0]['dynamodb']['NewImage']['id']['S']
        assert job['payload'] == ddb_job_created_valid['Records'][0]['dynamodb']['NewImage']['payload']['S']

    def test_sqs_job_created_consumed(self, card_statements_valid, sqs_job_created_valid, events_consumers_job_service,
                                      bank_statements_data_repo):
        bank_statements_data_repo.save.return_value = 'test_file.json'
        app.lambda_handler(sqs_job_created_valid, [])
        print(events_consumers_job_service.save.call_args)
        in_progress_job = events_consumers_job_service.save.call_args_list[0][0][0]
        assert in_progress_job.status == JobStatus.IN_PROGRESS
        completed_job = events_consumers_job_service.save.call_args_list[1][0][0]
        assert completed_job.status == JobStatus.COMPLETED
        job_result = json.loads(completed_job.result)
        assert job_result['collect']['downloaded_files'][0] == 'test_file.json'

    def test_sqs_job_created_transform(self, card_statements_valid, sqs_job_created_transform_valid,
                                       events_consumers_job_service, tabula_mock, pdf_mock, file_mock,
                                       bank_statements_data_repo, bank_statement_df_valid):
        bank_statements_data_repo.save.return_value = 'test_file.json'
        app.lambda_handler(sqs_job_created_transform_valid, [])
        print(events_consumers_job_service.save.call_args)
        in_progress_job = events_consumers_job_service.save.call_args_list[0][0][0]
        assert in_progress_job.status == JobStatus.IN_PROGRESS
        completed_job = events_consumers_job_service.save.call_args_list[1][0][0]
        assert completed_job.status == JobStatus.COMPLETED
        job_result = json.loads(completed_job.result)
        assert job_result['transform'][0]['test_transform.pdf']['status'] == 'success'
