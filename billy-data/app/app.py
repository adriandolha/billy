import json

from billy_data import LOGGER
from billy_data.bank_statements import BankStatementService, SearchCriteria
from billy_data.config import get_config
from billy_data.app_context import app_context
from billy_data.events_consumers import handle
from billy_data.job import Job
from billy_data.provider import bank_statement_provider_service
from boto3.dynamodb.types import TypeDeserializer
from billy_data.events import Event, publish, Events

config = get_config()
deserializer = TypeDeserializer()


def lambda_handler(event, context):
    LOGGER.info(event)
    LOGGER.info(context)
    if event.get('Records') is not None:
        return handle_records(event, context)
    if event.get('op') == 'process':
        return process(event, context)

    if event.get('op') == 'transform':
        return transform(event, context)


def handle_records(event, context):
    records = event.get('Records')
    for record in records:
        if record.get('eventSource') == 'aws:dynamodb':
            LOGGER.info('New dynamo stream records...')
            handle_dynamo(record, event, context)
        if record.get('eventSource') == 'aws:sqs':
            LOGGER.info('New sqs records...')
            handle_sqs(record, event, context)


def handle_dynamo(record, event, context):
    if record.get('eventName') == 'INSERT':
        LOGGER.debug('New dynamo stream insert event...')
        LOGGER.debug(record)

        new_image = record.get('dynamodb').get('NewImage')
        if str(new_image.get('pk')['S']).startswith('user#') and str(new_image.get('sk')['S']).startswith('job#'):
            handle_ddb_job_created(new_image)


def handle_sqs(record, event, context):
    body = json.loads(record.get('body'))
    attrs = body.get('MessageAttributes')
    LOGGER.info('Message attributes...')
    LOGGER.info(attrs)
    if attrs.get('event_name'):
        event_name = attrs.get('event_name')['Value']
        LOGGER.info(f'New event {event_name}')
        payload = body.get('Message')
        handle(Event(name=event_name, payload=payload))


def handle_ddb_job_created(new_image):
    _new_image = {k: deserializer.deserialize(v) for k, v in new_image.items()}
    job = Job.from_dict(_new_image)
    LOGGER.info(job)
    event = Event(name=Events.JOB_CREATED.value, payload=job.to_json())
    publish(event)


def process(event, context):
    _config = get_config()
    username = event['username']
    app_context.username = username
    search_criteria = event['search_criteria']
    _search_criteria = SearchCriteria()
    search_criterias = None
    if search_criteria.get('subjects'):
        search_criterias = ' '.join([_search_criteria.subject(search_criteria['subjects'])])
    if search_criteria.get('since'):
        search_criterias = ' '.join([search_criterias, _search_criteria.since(search_criteria['since'])])
    if search_criterias is None:
        search_criterias = _search_criteria.all_data()
    provider = bank_statement_provider_service.get_all()[0]

    downloaded_files = BankStatementService(user=provider.yahoo_user,
                                            password=provider.yahoo_password,
                                            host=provider.yahoo_host,
                                            port=provider.yahoo_port,
                                            card_statement_pdf_password=provider.card_statement_pdf_password
                                            ).collect(
        search_criterias)
    return {
        "statusCode": 200,
        "body": json.dumps({'collect': {'downloaded_files': downloaded_files}}),
    }


def transform(event, context):
    _config = get_config()
    username = event['username']
    app_context.username = username
    file = event['file']
    provider = bank_statement_provider_service.get_all()[0]

    result = BankStatementService(user=provider.yahoo_user,
                                  password=provider.yahoo_password,
                                  host=provider.yahoo_host,
                                  port=provider.yahoo_port,
                                  card_statement_pdf_password=provider.card_statement_pdf_password).transform(file)

    return {
        "statusCode": 200,
        "body": json.dumps(result),
    }
