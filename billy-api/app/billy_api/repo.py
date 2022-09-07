from __future__ import annotations
import json
import os.path
from io import BytesIO
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

from billy_api import LOGGER
from billy_api.config import get_config
from abc import ABC, abstractmethod
from billy_api.app_context import app_context


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

    @abstractmethod
    def read_stream(self, file_name: str) -> BytesIO:
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

    def list_files(self, key):
        LOGGER.info(f'Listing files under {key}')
        if not str(key).endswith('/'):
            key = f'{key}/'
        files = []
        for file in self.bucket.objects.all():
            # LOGGER.debug(file.key)
            if key in file.key:
                files.append(file.key)
        return files

    def get(self, file_name: str):
        LOGGER.debug(f'Reading file {file_name} from s3.')
        s3_file = self.s3.Object(self.bucket_name, file_name)
        body = s3_file.get()['Body'].read()
        file_content = body.decode('utf-8')
        # LOGGER.debug(file_content)
        return file_content

    def read_stream(self, file_name: str):
        s3_file = self.s3.Object(self.bucket_name, file_name)
        bytes_stream = BytesIO(s3_file.get()['Body'].read())
        return bytes_stream

    def read(self, file_name: str):
        s3_file = self.s3.Object(self.bucket_name, file_name)
        bytes = s3_file.get()['Body'].read()
        return bytes

    def abs_path(self, *paths) -> str:
        return '/'.join([app_context.username, *paths])

    def create_if_not_exists(self, *abs_paths):
        pass

    def exists(self, path) -> bool:
        objs = list(self.bucket.objects.filter(Prefix=path))
        return any([w.key == path for w in objs])

    def presigned_url(self, key: str, expiration: int = 3600):
        s3_client = boto3.client('s3')
        response = s3_client.generate_presigned_url('put_object',
                                                    Params={'Bucket': self.bucket_name,
                                                            'Key': key},
                                                    ExpiresIn=expiration)
        LOGGER.debug(response)
        return response


config = get_config()
data_repo = S3DataRepo(config['data_bucket'])
