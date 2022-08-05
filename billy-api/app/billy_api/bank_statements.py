from dataclasses import dataclass
from functools import lru_cache
import os
import numpy as np

from billy_api import LOGGER
from billy_api.config import get_config
from billy_api.repo import DataRepo, S3DataRepo
import pandas as pd
from billy_api.app_context import app_context

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


@lru_cache()
def get_data_df() -> pd.DataFrame():
    config = get_config()
    s3_repo = S3DataRepo(config['data_bucket'])
    data_file = config['bank_statements_data_file']
    LOGGER.info(f'Reading data from {data_file}')
    data = s3_repo.get(f'{app_context.username}/{data_file}')
    df = pd.read_json(data)
    return df


class BankStatementApi:
    def __init__(self):
        self.config = get_config()
        self.s3_repo = S3DataRepo(self.config['data_bucket'])
        self.data_file = self.config['bank_statements_data_file']

    def search_for_word(self, word:str, df: pd.DataFrame):
        mask = np.column_stack(
            [df[col].astype(str).str.lower().str.contains(word, na=False) for col in df])
        return df.loc[mask.any(axis=1)]

    def search(self, query: str, limit: int = 10, offset: int = 0) -> SearchResult:
        _df = get_data_df()
        total=len(_df)
        LOGGER.info(f'query={query}, offset={offset}, limit={limit}')
        # LOGGER.debug(_df.to_string())

        if len(_df) > 0:
            queries = query.split(" ")
            for q in queries:
                LOGGER.debug(f'Searching for {q}')
                _df = self.search_for_word(q, _df)
        LOGGER.info(f"Get paginated result...")
        search_count = len(_df)
        _df = _df.sort_values(by='date', ascending=False).iloc[offset:offset + limit]
        LOGGER.info(f"Convert date column to string...")
        _df['date'] = _df['date'].astype(str)
        LOGGER.info(f"Return result...")
        return SearchResult(columns=_df.columns.values.tolist(), items=_df.values.tolist(), total=total,
                            search_count=search_count)
