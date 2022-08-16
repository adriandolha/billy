from billy_data.bank_statements import create_data_paths
from billy_data.category import CategoryService
from billy_data.config import get_config


def setup():
    create_data_paths()
    config = get_config()
    CategoryService().load_from_file(config['categories_file'])
