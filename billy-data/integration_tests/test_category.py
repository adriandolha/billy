from billy_data.category import CategoryService
import requests


class TestCategories:
    def test_category_load_from_file(self, config_valid):
        _categories = CategoryService().get_all()
        categories = [c.name for c in _categories]
        assert 'food' in categories

    def test_category_data_is_not_public(self, config_valid):
        response = requests.get(f'https://s3.eu-central-1.amazonaws.com/{config_valid["data_bucket"]}/categories.json')
        assert response.status_code == 403

    def test_bank_statements_data_file_is_not_public(self, config_valid):
        response = requests.get(
            f'https://s3.eu-central-1.amazonaws.com/{config_valid["data_bucket"]}/bank_statements/data.json')
        assert response.status_code == 403
