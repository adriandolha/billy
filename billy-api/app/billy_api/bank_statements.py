import uuid
from dataclasses import dataclass
from functools import lru_cache
import os
import numpy as np
import boto3
from billy_api import LOGGER
from billy_api.config import get_config
from billy_api.repo import DataRepo, S3DataRepo
import pandas as pd
from billy_api.app_context import app_context

ddb = boto3.resource('dynamodb')


@dataclass
class DataPaths:
    root: str
    raw: str
    no_pass: str
    tables: str
    data: str
    all_data: str

    def get_path_from_base_name_or_abs_path(self, data_path: str, file_name: str) -> str:
        base_name = os.path.basename(file_name)
        return os.path.join(data_path, base_name)

    def raw_file(self, file_name: str) -> str:
        return self.get_path_from_base_name_or_abs_path(self.raw, file_name)

    def no_pass_file(self, file_name: str) -> str:
        return self.get_path_from_base_name_or_abs_path(self.no_pass, file_name)

    def tables_file(self, file_name: str) -> str:
        return self.get_path_from_base_name_or_abs_path(self.tables, file_name)

    def data_file(self, file_name: str) -> str:
        return self.get_path_from_base_name_or_abs_path(self.data, file_name)

    def dirs(self):
        return [v for k, v in self.__dict__.items() if k != 'all_data']


def data_paths(data_repo: DataRepo) -> DataPaths:
    return DataPaths(
        root=data_repo.abs_path('bank_statements'),
        raw=data_repo.abs_path('bank_statements', 'raw'),
        no_pass=data_repo.abs_path('bank_statements', 'no_pass'),
        tables=data_repo.abs_path('bank_statements', 'tables'),
        data=data_repo.abs_path('bank_statements', 'data'),
        all_data=data_repo.abs_path('bank_statements', 'data.json'),
    )


@dataclass
class SearchResult:
    columns: list
    search_count: int
    total: int
    items: list

    def to_dict(self):
        return self.__dict__


@lru_cache(maxsize=1)
def get_data_df_cached(last_updated: str = '0') -> pd.DataFrame():
    LOGGER.debug(f'Caching data for last_update {last_updated}')
    config = get_config()
    s3_repo = S3DataRepo(config['data_bucket'])
    data_file = f'{app_context.username}/bank_statements/data.json'
    if not s3_repo.exists(data_file):
        return pd.DataFrame(columns=['category', 'date', 'desc', 'suma'], data=[])
    LOGGER.info(f'Reading data from {data_file}')
    data = s3_repo.get(data_file)
    df = pd.read_json(data)
    return df


def get_data_df() -> pd.DataFrame():
    username = app_context.username
    data_table = get_config()['ddb_table']
    LOGGER.info(f'Searching bank_statement_data last_update for user {username}...')
    print(ddb)
    response = ddb.Table(data_table).get_item(Key={'pk': f'user#{username}', 'sk': 'bank_statement_data'})
    LOGGER.debug(response)
    item = response.get('Item')
    last_updated = '0'
    if item is not None:
        last_updated = item.get('last_updated')
        LOGGER.info(f'Last updated is {last_updated}')
    return get_data_df_cached(last_updated)


class BankStatementApi:
    def __init__(self):
        self.config = get_config()
        self.s3_repo = S3DataRepo(self.config['data_bucket'])
        self.data_file = self.config['bank_statements_data_file']

    def search_for_word(self, word: str, df: pd.DataFrame):
        mask = np.column_stack(
            [df[col].astype(str).str.lower().str.contains(word.lower(), na=False) for col in df])
        return df.loc[mask.any(axis=1)]

    def search_df(self, df: pd.DataFrame, query: str):
        _df = df
        if len(df) > 0:
            queries = query.split(" ")
            for q in queries:
                LOGGER.debug(f'Searching for {q}')
                _df = self.search_for_word(q, _df)
        return _df

    def search(self, query: str, limit: int = 10, offset: int = 0) -> SearchResult:
        _df = get_data_df()
        total = len(_df)
        LOGGER.info(f'query={query}, offset={offset}, limit={limit}')
        # LOGGER.debug(_df.to_string())
        _df = self.search_df(_df, query)
        LOGGER.info(f"Get paginated result...")
        search_count = len(_df)
        _df = _df.sort_values(by='date', ascending=False).iloc[offset:offset + limit]
        LOGGER.info(f"Convert date column to string...")
        _df['date'] = _df['date'].astype(str)
        LOGGER.info(f"Return result...")
        return SearchResult(columns=_df.columns.values.tolist(), items=_df.values.tolist(), total=total,
                            search_count=search_count)

    def upload_url(self):
        key_id = str(uuid.uuid4())
        key = f'{app_context.username}/upload/{key_id}.pdf'
        LOGGER.info(f'Presigned key is {key}')
        _upload_url = self.s3_repo.presigned_url(key=key)
        return {'upload_url': _upload_url, 'key': key}
