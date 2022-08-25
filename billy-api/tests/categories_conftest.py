import pytest
from mock import mock

from billy_api.category import CategoryService


@pytest.fixture()
def categories_table_mock():
    with mock.patch('billy_api.category.boto3') as boto_mock:
        with mock.patch('billy_api.category.Key') as _Key:
            yield boto_mock


@pytest.fixture()
def category_service_mock(categories_table_mock):
    _service = CategoryService()
    with mock.patch('billy_api.routes.categories.category_service', _service):
        _service.table = categories_table_mock
        yield _service
