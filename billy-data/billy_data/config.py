import os
from functools import lru_cache

from billy_data import LOGGER

DEFAULT_CONFIGS = {
    'connection_pool_minconn': 30,
    'connection_pool_maxconn': 40
}


@lru_cache()
def get_config():
    _config = dict(DEFAULT_CONFIGS)
    _config.update({
        'ddb_table': os.getenv('ddb_table', default='billy-dev'),
        'data_store_path': os.getenv('data_store_path', default=os.path.expanduser('billy_data')),
        'data_bucket': os.getenv('data_bucket', default='billy-data.adolha'),
        'yahoo_user': os.getenv('yahoo_user', default='yahoo_user'),
        'yahoo_password': os.getenv('yahoo_password', default='yahoo_password'),
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
