import dataclasses
import boto3
from boto3.dynamodb.conditions import Key
import base64
from billy_data import LOGGER
from billy_data.app_context import app_context
from billy_data.config import get_config


@dataclasses.dataclass
class BankStatementProvider:
    id: str
    provider_type: str
    yahoo_user: str
    yahoo_password: str
    yahoo_host: str
    card_statement_pdf_password: str
    yahoo_port: int

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(data: dict):
        return BankStatementProvider(id=data['id'],
                                     provider_type=data['provider_type'],
                                     yahoo_user=data['yahoo_user'],
                                     yahoo_password=data['yahoo_password'],
                                     yahoo_host=data['yahoo_host'],
                                     yahoo_port=int(data['yahoo_port']),
                                     card_statement_pdf_password=data['card_statement_pdf_password']
                                     )


class BankStatementProviderService:
    def __init__(self):
        self.config = get_config()
        self.ddb = boto3.resource('dynamodb')
        self.table = self.ddb.Table(get_config()['ddb_table'])

    def get_all(self) -> list[BankStatementProvider]:
        username = app_context.username
        LOGGER.debug(f'Get all jobs for user {username}')
        response = self.table.query(KeyConditionExpression=Key('pk').eq(f'user#{username}')
                                                           & Key('sk').begins_with('bank_statement_provider#')
                                    )
        return [BankStatementProvider.from_dict(_provider) for _provider in response['Items']]

    def save(self, provider: BankStatementProvider):
        item = {
            'pk': f'user#{app_context.username}',
            'sk': f'bank_statement_provider#{provider.id}',
            'lsi1_sk': f'status#{str(provider.provider_type)}',
            **provider.to_dict()
        }
        LOGGER.debug(f'Adding bank statement provider {provider.provider_type}')
        response = self.table.put_item(
            Item=item
        )
        LOGGER.debug(response)

        return provider


bank_statement_provider_service = BankStatementProviderService()
