import json

from billy_data import LOGGER
from billy_data.bank_statements import BankStatementService, SearchCriteria
from billy_data.config import get_config
from billy_data.app_context import app_context
from billy_data.provider import bank_statement_provider_service

def lambda_handler(event, context):
    LOGGER.info(event)
    LOGGER.info(context)
    if event.get('op') == 'collect':
        return collect(event, context)

    if event.get('op') == 'transform':
        return transform(event, context)


def collect(event, context):
    _config = get_config()
    yahoo_config = {'user': _config['yahoo_user'],
                    'password': _config['yahoo_password'],
                    'host': _config['yahoo_host'],
                    'port': _config['yahoo_port'],
                    'card_statement_pdf_password': _config['card_statement_pdf_password']}
    LOGGER.debug(yahoo_config)
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
        "body": json.dumps({'downloaded_files': downloaded_files}),
    }


def transform(event, context):
    _config = get_config()
    yahoo_config = {'user': _config['yahoo_user'],
                    'password': _config['yahoo_password'],
                    'host': _config['yahoo_host'],
                    'port': _config['yahoo_port'],
                    'card_statement_pdf_password': _config['card_statement_pdf_password']}
    LOGGER.debug(yahoo_config)
    username = event['username']
    app_context.username = username
    file = event['file']
    result = BankStatementService(**yahoo_config).transform(file)
    return {
        "statusCode": 200,
        "body": json.dumps(result),
    }
