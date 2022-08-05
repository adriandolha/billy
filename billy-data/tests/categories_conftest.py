import json

import numpy as np
import pandas as pd
import pytest
from mock import mock, MagicMock


@pytest.fixture()
def category_file_mock():
    with mock.patch('billy_data.category.open') as _mock:
        yield _mock


@pytest.fixture()
def categories_s3_mock(categories):
    with mock.patch('billy_data.category.S3DataRepo') as _mock:
        _mock.return_value.get.return_value = json.dumps(categories)
        yield _mock


@pytest.fixture()
def ddb_table_mock(app_valid):
    with mock.patch('boto3.resource') as ddb:
        table = MagicMock()
        ddb.return_value.Table.return_value = table
        yield table


@pytest.fixture()
def categories(ddb_table_mock):
    _categories = [{
        'name': 'food',
        'key_words': ['glovo']
    }, {
        'name': 'phone',
        'key_words': ['orange']
    }]
    ddb_table_mock.query.return_value = {'Items': _categories}
    return _categories


@pytest.fixture()
def bank_statement_categories(pd_read_csv):
    df = pd.DataFrame([
        ['Extras de cont Star Gold', '', ''],
        ['01 APR 2022 - 30 APR 2022', '', ''],
        ['ADRIAN DOLHA', np.nan, np.nan],
        ['Cumparaturi la parteneri Star Card', np.nan, np.nan],
        ['DATA DESCRIERE', '', ''],

        ['01-APR', 'Glovo desc', '-1,0'],
        ['01-APR', 'ORANGE', '-1,0'],
        ['Alte tranzactii', np.nan, np.nan],
        ['Sumar tranzactii', np.nan, np.nan],
    ], columns=['Unnamed: 0', 'Unnamed: 1', 'Unnamed: 2'])
    pd_read_csv.return_value = df
    yield df
