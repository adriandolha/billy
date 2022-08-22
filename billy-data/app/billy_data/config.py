import os
from functools import lru_cache

from billy_data import LOGGER

DEFAULT_CONFIGS = {
}


@lru_cache()
def get_config():
    _config = dict(DEFAULT_CONFIGS)
    LOGGER.debug(os.environ)
    _config.update({
        'ddb_table': os.getenv('ddb_table', default='billy-data-dev'),
        'sns_topic': os.getenv('sns_topic', default='sns_topic'),
        'data_store_path': os.getenv('data_store_path', default=os.path.expanduser('billy_data')),
        'data_bucket': os.getenv('data_bucket', default='data_bucket'),
        'yahoo_user': os.getenv('yahoo_user', default='yahoo_user'),
        'yahoo_password': os.getenv('yahoo_password', default='yahoo_pwd'),
        'yahoo_host': os.getenv('yahoo_host', default='yahoo_host'),
        'yahoo_port': int(os.getenv('yahoo_port', default='993')),
        'categories_file': os.getenv('categories_file', default='categories.json'),
        'card_statement_pdf_password': os.getenv('card_statement_pdf_password', default='card_statement_pdf_password')
    })
    LOGGER.debug('Configuration is:')
    for config_name in _config.keys():
        if 'password' not in config_name:
            LOGGER.debug(f'{config_name}={_config[config_name]}')
    return _config


CONFIG = get_config()
