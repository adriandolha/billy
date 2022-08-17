from __future__ import annotations
import json
import os.path
from pathlib import Path

import boto3

from billy_data import LOGGER
from billy_data.config import get_config
from abc import ABC, abstractmethod
from billy_data.app_context import app_context


class DataRepo(ABC):
    @abstractmethod
    def save(self, file_name: str, data: bytes):
        pass

    @abstractmethod
    def get(self, file_name: str):
        pass

    @abstractmethod
    def abs_path(self, *paths) -> str:
        pass

    @abstractmethod
    def create_if_not_exists(self, *abs_paths):
        pass


class LocalDataRepo(DataRepo):
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
        self.bucket = self.s3.Bucket(bucket_name)

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

    def abs_path(self, *paths) -> str:
        return '/'.join([app_context.username, *paths])

    def create_if_not_exists(self, *abs_paths):
        pass

    def exists(self, path) -> bool:
        objs = list(self.bucket.objects.filter(Prefix=path))
        return any([w.key == path for w in objs])


config = get_config()
data_repo = S3DataRepo(config['data_bucket'])
