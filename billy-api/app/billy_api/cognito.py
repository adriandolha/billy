import boto3
import botocore

from billy_api import LOGGER
from billy_api.auth import Group

class CognitoClient:
    def __init__(self):
        self.cognito_idp = boto3.client('cognito-idp')

    def confirm_user(self, user, password: str, user_pool_id_):
        LOGGER.info(f'Set password for user {user}.')
        response = self.cognito_idp.admin_set_user_password(
            UserPoolId=user_pool_id_,
            Username=user,
            Password=password,
            Permanent=True
        )
        LOGGER.debug(response)

    def add_user_to_group(self, user, user_pool_id_, group):
        LOGGER.info(f'Adding user {user} to group {group.name}.')
        response = self.cognito_idp.admin_add_user_to_group(
            UserPoolId=user_pool_id_,
            Username=user,
            GroupName=group.name
        )
        return response

    def create_cognito_user(self, user, user_pool_id_):
        try:
            response = self.cognito_idp.admin_get_user(
                UserPoolId=user_pool_id_,
                Username=user
            )
            LOGGER.debug(response)
        except botocore.exceptions.ClientError as error:
            LOGGER.info(f'User {user} not found.')
            LOGGER.info(f'Creating user {user}.')
            response = self.cognito_idp.admin_create_user(
                UserPoolId=user_pool_id_,
                Username=user,
                # UserAttributes=[{'Name': 'email', 'Value': }]
            )
            LOGGER.debug(response)
        return response.get('Username')

    def create_cognito_group(self, user_pool_id_, group: Group):
        try:
            response = self.cognito_idp.get_group(GroupName=group.name,
                                                  UserPoolId=user_pool_id_)
            LOGGER.debug(response)
        except botocore.exceptions.ClientError as error:
            LOGGER.error(error, exc_info=True)
            LOGGER.info(f'Group {group.name} not found.')
            LOGGER.info(f'Creating group {group.name}.')
            response = self.cognito_idp.create_group(
                GroupName=group.name,
                UserPoolId=user_pool_id_,
                Description='Users group.'
            )
            LOGGER.debug(response)
