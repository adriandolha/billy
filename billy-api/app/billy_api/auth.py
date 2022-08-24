from __future__ import annotations
import dataclasses
import json
from enum import Enum
from functools import lru_cache
import urllib.parse
import boto3
from authlib.jose import jwt
import requests
from billy_api import LOGGER
from billy_api.config import get_config
from billy_api.exceptions import AuthenticationException
from billy_api.app_context import app_context
from billy_api.config import CONFIG

cognito_idp = boto3.client('cognito-idp')


@dataclasses.dataclass
class Permission:
    name: str
    resource: str

    @property
    def full_name(self):
        return f'{self.resource}:{self.name}'

    def to_dict(self):
        return {
            'name': self.name,
            'resource': self.resource,
            'full_name': self.full_name,
        }

    @staticmethod
    def from_dict(data: dict) -> Permission:
        return Permission(name=data['name'], resource=data['resource'])


class Permissions(Enum):
    JOB_READ = Permission(resource='job', name='read')
    JOB_ADD = Permission(resource='job', name='add')
    JOB_UPDATE = Permission(resource='job', name='update')
    JOB_DELETE = Permission(resource='job', name='delete')
    BANK_STATEMENT_READ = Permission(resource='bank_statement', name='read')
    BANK_STATEMENT_ADD = Permission(resource='bank_statement', name='add')
    BANK_STATEMENT_UPDATE = Permission(resource='bank_statement', name='update')
    BANK_STATEMENT_DELETE = Permission(resource='bank_statement', name='delete')
    CATEGORY_READ = Permission(resource='category', name='read')
    CATEGORY_ADD = Permission(resource='category', name='add')
    CATEGORY_UPDATE = Permission(resource='category', name='update')
    CATEGORY_DELETE = Permission(resource='category', name='delete')


def permissions_values(permissions: list[Permissions]) -> list[Permission]:
    return [p.value for p in permissions]


def all_permissions() -> list[Permission]:
    return [p.value for p in Permissions]


def read_permissions() -> list[Permission]:
    return permissions_values([
        Permissions.BANK_STATEMENT_READ,
        Permissions.CATEGORY_READ,
        Permissions.JOB_READ,
    ])


@dataclasses.dataclass
class Group:
    name: str
    permissions: list[Permission]

    def to_dict(self):
        return {
            'name': self.name,
            'permissions': [permission.to_dict() for permission in self.permissions]
        }

    @staticmethod
    def from_dict(data: dict) -> Group:
        return Group(name=data['name'], permissions=[Permission.from_dict(perm) for perm in data['permissions']])


class Groups(Enum):
    USERS = Group('Users', permissions=read_permissions())
    VERIFIED_USERS = Group('VerifiedUsers', permissions=all_permissions())
    DEMO_USERS = Group('DemoUsers', read_permissions())

    @staticmethod
    def find_group(group_name: str) -> Group:
        _groups = [g for g in Groups if g.name == group_name]
        return _groups[0] if len(_groups) > 0 else None


@dataclasses.dataclass
class User:
    username: str
    group: Group


class AuthService:
    def __init__(self):
        self.ddb = boto3.resource('dynamodb')
        data_table = get_config()['ddb_table']
        self.table = self.ddb.Table(data_table)

    def add_group(self, group: Group):
        LOGGER.info(f'Adding group {group.name}...')
        response = self.table.put_item(
            Item={
                'pk': f'group#{group.name}',
                'sk': 'group',
                **group.to_dict()
            }
        )
        LOGGER.debug(response)
        return group

    def get_group(self, name: str):
        LOGGER.info(f'Get group {name}...')
        response = self.table.get_item(
            Key={
                'pk': f'group#{name}',
                'sk': 'group'
            }
        )
        LOGGER.debug(response)
        _group = response.get('Item')
        return Group.from_dict(_group) if _group is not None else None


def id_token_for_client_credentials(username, password, client_id):
    response = cognito_idp.initiate_auth(
        ClientId=client_id,
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={"USERNAME": username,
                        "PASSWORD": password},
    )
    LOGGER.debug(response)
    id_token = response["AuthenticationResult"]["IdToken"]
    print(f'Cognito id token {id_token}')
    return id_token


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
            LOGGER.debug(payload)
            username_ = payload['cognito:username']
            app_context.username = username_
            if payload.get('cognito:groups'):
                group_name = payload.get('cognito:groups')[0]
                LOGGER.info(f'Payload user is {username_} and user group is {group_name}')
                app_context.user = User(username=username_, group=Groups.find_group(group_name))
            LOGGER.info(f'Token user is {app_context.username}')
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
