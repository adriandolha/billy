import json
from functools import lru_cache
import urllib.parse

from authlib.jose import jwt
import requests
from billy_api import LOGGER
from billy_api.config import get_config
from billy_api.exceptions import AuthenticationException
from billy_api.app_context import app_context


@lru_cache()
def jwk():
    config = get_config()
    region = config['region']
    user_pool_id = config['cognito_user_pool_id']
    cognito_jwk_url = f'https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json'
    LOGGER.info(f'Reading JWK from {cognito_jwk_url}')
    response = requests.get(cognito_jwk_url)
    key = json.loads(response.content)
    LOGGER.info(f'Cognito jwk is {key}')
    return key


def requires_permission():
    def requires_permission_decorator(function):
        def wrapper(*args, **kwargs):
            event = args[0] if args and len(args) > 0 else kwargs['event']
            LOGGER.info(f'Authorization...\n{event.get("headers")}')
            authorization_header = event.get("headers").get('Authorization')
            if authorization_header is None:
                raise AuthenticationException()
            payload = jwt.decode(authorization_header, jwk())
            # LOGGER.info(payload)
            app_context.username = payload['cognito:username']
            LOGGER.info('Decoded jwt...')
            _result = function(*args, **kwargs)
            return _result

        wrapper.__name__ = function.__name__
        return wrapper

    return requires_permission_decorator


def sign_in_cognito(event, context):
    LOGGER.info(event)
    LOGGER.info(context)
    config = get_config()
    cognito_domain = config['cognito_domain']
    cognito_client_id = config['cognito_client_id']
    cognito_redirect_uri = urllib.parse.quote(config['cognito_redirect_uri'], safe='')
    cognito_url = f'{cognito_domain}/login?' \
                  f'client_id={cognito_client_id}' \
                  f'&response_type=code&' \
                  f'&scope=openid+email+phone+profile' \
                  f'&redirect_uri={cognito_redirect_uri}'
    LOGGER.info(f'Cognito login url {cognito_url}')
    return {
        "statusCode": 302,
        "headers": {'Location': cognito_url},
    }


def get_token(event, context):
    LOGGER.info(event)
    LOGGER.info(context)
    config = get_config()
    code = event['queryStringParameters']['code']
    cognito_domain = config['cognito_domain']
    cognito_client_id = config['cognito_client_id']
    # cognito_redirect_uri = urllib.parse.quote(config['cognito_redirect_uri'], safe='')
    cognito_redirect_uri = config['cognito_redirect_uri']
    cognito_url = f'{cognito_domain}/oauth2/token?'
    LOGGER.info(f'Cognito token url {cognito_url}')
    token_request_data = {'client_id': cognito_client_id,
                          'grant_type': 'authorization_code',
                          'code': code,
                          'redirect_uri': cognito_redirect_uri}
    LOGGER.info(f'Cognito token request data {token_request_data}')

    response = requests.post(cognito_url,
                             data=token_request_data,
                             headers={'Content-Type': 'application/x-www-form-urlencoded'})
    LOGGER.info(f'Cognito response {response.content}')
    if response.status_code != 200:
        return {
            "statusCode": 403,
            'body': 'Unauthorized',
        }

    return {
        "statusCode": 200,
        'body': response.content.decode('utf-8'),
    }
