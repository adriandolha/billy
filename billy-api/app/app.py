import json

from billy_api import LOGGER
from billy_api.bank_statements import BankStatementApi
from billy_api.auth import requires_permission, sign_in_cognito, get_token
from billy_api.exceptions import AuthenticationException
from billy_api.stats import StatsApi


@requires_permission()
def search(event, context):
    LOGGER.info(event)
    LOGGER.info(context)
    query = event["queryStringParameters"]['query']
    limit = int(event["queryStringParameters"].get('limit') or 10)
    offset = int(event["queryStringParameters"].get('offset') or 0)
    LOGGER.info(f'query={query}, offset={offset}, limit={limit}')
    search_result = BankStatementApi().search(query=query, offset=offset, limit=limit)
    LOGGER.info(f'Found {search_result.search_count} entries')
    return {
        "statusCode": 200,
        "body": json.dumps(search_result.to_dict()),
    }


@requires_permission()
def expenses_per_month(event, context):
    LOGGER.info(event)
    LOGGER.info(context)
    LOGGER.info(f'Get stats...')
    result = StatsApi().expenses_per_month()
    return {
        "statusCode": 200,
        "body": json.dumps(result),
    }


@requires_permission()
def expenses_per_month_and_category(event, context):
    LOGGER.info(event)
    LOGGER.info(context)
    LOGGER.info(f'Get stats...')
    result = StatsApi().expenses_per_month_and_category()
    return {
        "statusCode": 200,
        "body": json.dumps(result),
    }


def lambda_handler(event, context):
    event_path = event['path']
    http_method = event['requestContext']['httpMethod']
    cors_headers = {
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "*"
    }

    if str(http_method).lower() == 'options':
        return {
            "statusCode": 200,
            "body": json.dumps('ok'),
            'headers': cors_headers
        }

    result = None
    try:
        result = handle_request(context, event, event_path, result)
    except AuthenticationException as auth_exception:
        result = {
            "statusCode": 401,
            "body": json.dumps(f'{auth_exception.message}'),
        }

    if not result:
        result = {
            "statusCode": 404,
            "body": json.dumps(f'Unsupported request for path {event_path}'),
        }
    cors_response = {'headers': cors_headers, **result}
    return cors_response


def handle_request(context, event, event_path, result):
    if event_path == '/billy/bank_statements/search':
        result = search(event, context)
    if event_path == '/billy/stats/expenses_per_month':
        result = expenses_per_month(event, context)
    if event_path == '/billy/stats/expenses_per_month_and_category':
        result = expenses_per_month_and_category(event, context)
    if event_path == '/billy/auth/sign_in/cognito':
        result = sign_in_cognito(event, context)
    if event_path == '/billy/auth/token/cognito':
        result = get_token(event, context)
    return result
