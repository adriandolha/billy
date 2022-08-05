import json
import os.path

from mock.mock import MagicMock

from billy_data.category import CategoryService
from categories_conftest import *


class TestCategory:
    def test_category_load_from_file(self, category_file_mock, categories, categories_s3_mock):
        _mock = MagicMock()
        category_file_mock.return_value.__enter__.return_value = _mock
        _mock.read.return_value = json.dumps(categories)
        _categories = CategoryService().load_from_file(os.path.expanduser('categories.json'))
        assert _categories[0].name == 'food'
        assert _categories[0].key_words == ['glovo']

    def test_category_get_all(self, category_file_mock, categories):
        _categories = CategoryService().get_all()
        assert _categories[0].name == 'food'
        assert _categories[0].key_words == ['glovo']
