from __future__ import annotations
import datetime
import json

from billy_data import LOGGER
from billy_data.app_context import app_context
from billy_data.bank_statements import BankStatementService, SearchCriteria
from billy_data.events import Event, Events
from billy_data.job import Job, JobStatus, JobService
from billy_data.provider import BankStatementProviderService
from billy_data.job import job_service


def process(payload: dict) -> dict:
    search_criteria = payload['search_criteria']
    _search_criteria = SearchCriteria()
    search_criterias = None
    if search_criteria.get('subjects'):
        search_criterias = ' '.join([_search_criteria.subject(search_criteria['subjects'])])
    if search_criteria.get('since'):
        search_criterias = ' '.join([search_criterias, _search_criteria.since(search_criteria['since'])])
    if search_criterias is None:
        search_criterias = _search_criteria.all_data()
    provider = BankStatementProviderService().get_all()[0]

    bank_statement_service = BankStatementService(user=provider.yahoo_user, password=provider.yahoo_password,
                                                  host=provider.yahoo_host,
                                                  port=provider.yahoo_port,
                                                  card_statement_pdf_password=provider.card_statement_pdf_password)
    downloaded_files = bank_statement_service.collect(
        search_criterias)
    transform_results = []
    for file in downloaded_files:
        try:
            transform_results.append(bank_statement_service.transform(file))
        except Exception as e:
            LOGGER.error(e)
    result = {'collect': {'downloaded_files': downloaded_files},
              'transform': transform_results}
    return result


def transform(payload: dict) -> dict:
    files = payload['files']
    provider = BankStatementProviderService().get_all()[0]

    bank_statement_service = BankStatementService(user=provider.yahoo_user, password=provider.yahoo_password,
                                                  host=provider.yahoo_host,
                                                  port=provider.yahoo_port,
                                                  card_statement_pdf_password=provider.card_statement_pdf_password)
    transform_results = []
    for file in files:
        try:
            transform_results.append({file: {'status': 'success',
                                             'result': bank_statement_service.transform(file)}})
        except Exception as e:
            transform_results.append({file: {'status': 'failed'}})
            LOGGER.error(e, exc_info=True)
    result = {'transform': transform_results}
    return result


def load(payload: dict) -> dict:
    files = payload['files']
    provider = BankStatementProviderService().get_all()[0]

    bank_statement_service = BankStatementService(user=provider.yahoo_user, password=provider.yahoo_password,
                                                  host=provider.yahoo_host,
                                                  port=provider.yahoo_port,
                                                  card_statement_pdf_password=provider.card_statement_pdf_password)
    load_result = []
    try:
        load_result.append({'status': 'success',
                            'result': bank_statement_service.load(files)})
    except Exception as e:
        load_result.append({'status': 'failed'})
        LOGGER.error(e, exc_info=True)
    result = {'load': load_result}
    return result


SUPPORTED_JOB_OP = {
    'process': process,
    'transform': transform,
    'load': load
}


def handle(event: Event):
    if event.name == Events.JOB_CREATED.value:
        job = Job.from_dict(json.loads(event.payload))
        job_payload = json.loads(job.payload)
        op = job_payload.get('op')
        if not (op in SUPPORTED_JOB_OP.keys()):
            LOGGER.error(f'Unsupported op {op}')
            return False
        username = job_payload['username']
        app_context.username = username
        job.status = JobStatus.IN_PROGRESS
        job_service.save(job)
        result = SUPPORTED_JOB_OP[op](json.loads(job.payload))
        job = Job.from_dict(job.to_dict())
        job.completed_at = datetime.datetime.now()
        job.status = JobStatus.COMPLETED
        job.result = json.dumps(result)
        job_service.save(job)
        LOGGER.info(f'Completed job {job.id}.')
