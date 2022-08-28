import dataclasses
from datetime import datetime
from functools import lru_cache

from billy_api import LOGGER
from billy_api.auth import Groups, AuthService
from billy_api.config import CONFIG
import boto3
import botocore

ddb = boto3.resource('dynamodb')


@dataclasses.dataclass
class AppInfo:
    created_at: datetime = datetime.now()

    def to_dict(self):
        return {'created_at': self.created_at.isoformat()}


@lru_cache()
def setup():
    data_table = CONFIG['ddb_table']
    LOGGER.info(f'Data table is {data_table}')
    ddb_table = ddb.Table(data_table)
    ddb_table.delete_item(Key={'pk': 'app', 'sk': 'info'})
    response = ddb_table.get_item(Key={'pk': 'app', 'sk': 'info'})
    LOGGER.debug(response)
    if response.get('Item'):
        LOGGER.info('App is setup and ready to use...')
    else:
        LOGGER.info('Running database setup...')
        app_setup = AppSetup(ddb_table)
        app_setup.save_app_info()
        app_setup.setup_cognito()
        app_setup.setup_users()


class AppSetup:
    def __init__(self, ddb_table):
        self.ddb_table = ddb_table
        self.cognito_idp = boto3.client('cognito-idp')
        self.auth_service = AuthService()

    def save_app_info(self):
        info = AppInfo()
        LOGGER.info(f'Saving app info {info.to_dict()}')
        response = self.ddb_table.put_item(Item={
            'pk': 'app',
            'sk': 'info',
            **info.to_dict()
        })
        LOGGER.debug(response)

    def setup_users(self):
        for group in Groups:
            if not self.auth_service.get_group(group.value.name):
                self.auth_service.add_group(group.value)
            else:
                LOGGER.info(f'Found group {group.value.name}.')

    def setup_cognito(self):
        LOGGER.info('Running cognito setup...')
        verified_users_group = Groups.VERIFIED_USERS.value
        user_pool_id_ = CONFIG['cognito_user_pool_id']
        self.create_cognito_group(user_pool_id_, verified_users_group)
        integration_user = 'integration_test_user@billy.com'
        self.create_cognito_user(integration_user, user_pool_id_)
        response = self.add_user_to_group(integration_user, user_pool_id_, verified_users_group)
        LOGGER.debug(response)
        self.confirm_user(integration_user, user_pool_id_)

    def confirm_user(self, integration_user, user_pool_id_):
        LOGGER.info(f'Set password for user {integration_user}.')
        response = self.cognito_idp.admin_set_user_password(
            UserPoolId=user_pool_id_,
            Username=integration_user,
            Password=CONFIG['cognito_user_password'],
            Permanent=True
        )
        LOGGER.debug(response)

    def add_user_to_group(self, integration_user, user_pool_id_, verified_users_group):
        LOGGER.info(f'Adding user {integration_user} to group {verified_users_group.name}.')
        response = self.cognito_idp.admin_add_user_to_group(
            UserPoolId=user_pool_id_,
            Username=integration_user,
            GroupName=verified_users_group.name
        )
        return response

    def create_cognito_user(self, integration_user, user_pool_id_):
        try:
            response = self.cognito_idp.admin_get_user(
                UserPoolId=user_pool_id_,
                Username=integration_user
            )
            LOGGER.debug(response)
        except botocore.exceptions.ClientError as error:
            LOGGER.info(f'User {integration_user} not found.')
            LOGGER.info(f'Creating user {integration_user}.')
            response = self.cognito_idp.admin_create_user(
                UserPoolId=user_pool_id_,
                Username=integration_user,
                # UserAttributes=[{'Name': 'email', 'Value': }]
            )
            LOGGER.debug(response)

    def create_cognito_group(self, user_pool_id_, verified_users_group):
        try:
            response = self.cognito_idp.get_group(GroupName=verified_users_group.name,
                                                  UserPoolId=user_pool_id_)
            LOGGER.debug(response)
        except botocore.exceptions.ClientError as error:
            LOGGER.error(error, exc_info=True)
            LOGGER.info(f'Group {verified_users_group.name} not found.')
            LOGGER.info(f'Creating group {verified_users_group.name}.')
            response = self.cognito_idp.create_group(
                GroupName=verified_users_group.name,
                UserPoolId=user_pool_id_,
                Description='Verified users group.'
            )
            LOGGER.debug(response)
