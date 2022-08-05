import os.path
from pathlib import Path

import boto3

from billy_api import LOGGER
from billy_api.config import get_config


class DataRepo:
    def __init__(self):
        self.config = get_config()
        self.data_store_path = os.path.abspath(self.config['data_store_path'])

    def create_if_not_exists(self, *abs_paths):
        for path in abs_paths:
            Path(path).mkdir(parents=True, exist_ok=True)
        return abs_paths

    def abs_path(self, *paths) -> str:
        return os.path.join(self.data_store_path, *paths)

    def save(self, file_name: str, data: bytes):
        to_file = self.abs_path(file_name) if not os.path.isabs(file_name) else file_name
        with open(to_file, 'wb') as file:
            file.write(data)
        return to_file


class S3DataRepo(DataRepo):
    def __init__(self, bucket_name):
        DataRepo.__init__(self)
        self.s3 = boto3.resource('s3')
        self.bucket_name = bucket_name

    def save(self, file_name: str, data: bytes):
        s3_file = self.s3.Object(self.bucket_name, file_name)
        s3_file.put(Body=data)
        return file_name

    def get(self, file_name: str):
        s3_file = self.s3.Object(self.bucket_name, file_name)
        body = s3_file.get()['Body'].read()
        file_content = body.decode('utf-8')
        LOGGER.debug(f'Reading file {file_name} from s3.')
        LOGGER.debug(file_content)
        return file_content
