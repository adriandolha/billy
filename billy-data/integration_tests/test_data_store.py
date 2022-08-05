import os

import pandas

from billy_data.bank_statements import BankStatementService, SearchCriteria, create_data_paths
from os import listdir
from os.path import isfile, join

from billy_data.repo import DataRepo

os.environ['env'] = 'test'


class TestDataStore:
    def ds_files(self, ds_path):
        return [f for f in listdir(ds_path) if isfile(join(ds_path, f))]

    def test_create_if_not_exists(self, config_valid, yahoo_config_valid):
        for abs_path in create_data_paths():
            assert os.path.exists(abs_path)
