import json
from dataclasses import dataclass

import boto3
from boto3.dynamodb.conditions import Key

from billy_api import LOGGER
from billy_api.app_context import app_context
from billy_api.config import get_config
from billy_api.repo import S3DataRepo


@dataclass
class Category:
    name: str
    key_words: list[str]

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(data: dict):
        return Category(**data)

    def __eq__(self, other):
        return self.name == other.name if other else False


class CategoryService:
    def __init__(self):
        self.config = get_config()
        self.bucket_name = self.config['data_bucket']
        self.s3_repo = S3DataRepo(self.bucket_name)
        self.ddb = boto3.resource('dynamodb')
        self.table = self.ddb.Table(get_config()['ddb_table'])

    def get_all(self) -> list[Category]:
        response = self.table.query(KeyConditionExpression=Key('pk').eq(f'user#{app_context.username}')
                                                           & Key('sk').begins_with('category#')
                                    )

        LOGGER.debug(f'Get all categories response: {response}')
        categories = []
        for _category in response['Items']:
            categories.append(Category(name=_category['name'], key_words=_category['key_words']))
        return categories

    def save(self, category: Category):
        categories = []
        item = {
            'pk': f'user#{app_context.username}',
            'sk': f'category#{category.name}',
            **category.to_dict()
        }
        LOGGER.debug(f'Adding category {item}')
        response = self.table.put_item(
            Item=item
        )
        # LOGGER.debug(response)

        return categories

    def load_from_file(self, file: str) -> list[Category]:
        file_content = self.s3_repo.get(file)
        categories = [Category.from_dict(data) for data in json.loads(file_content)]
        existing_categories = self.get_all()
        # LOGGER.debug(f'Existing categories:{existing_categories}')

        for category in categories:
            self.save(category)
        # LOGGER.debug(f'Categories:{categories}')
        return categories


category_service = CategoryService()
