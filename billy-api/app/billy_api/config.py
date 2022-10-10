import os
from functools import lru_cache

from billy_api import LOGGER

DEFAULT_CONFIGS = {
    'connection_pool_minconn': 30,
    'connection_pool_maxconn': 40
}


@lru_cache()
def get_config():
    _config = dict(DEFAULT_CONFIGS)

    _config.update({
        'data_store_path': os.getenv('data_store_path', default=os.path.expanduser('billy_data')),
        'data_bucket': os.getenv('data_bucket', default='billy-data.adolha'),
        'ddb_table': os.getenv('data_table', default='data_table'),
        'bank_statements_data_file': os.getenv('bank_statements_data_file', default='bank_statements/data.json'),
        'cognito_user_pool_id': os.getenv('cognito_user_pool_id', default='cognito_user_pool_id'),
        'region': os.getenv('region', default='region'),
        'cognito_domain': os.getenv('cognito_domain', default='amazoncognito'),
        'cognito_client_id': os.getenv('cognito_client_id', default='cognito_client_id'),
        'cognito_user': os.getenv('cognito_user', default='cognito_user'),
        'cognito_redirect_uri': os.getenv('cognito_redirect_uri', default='cognito_redirect_uri'),
        'cognito_user_password': os.getenv('cognito_user_password', default='cognito_user_password'),
        'log_level': os.getenv('log_level', default='ERROR'),
        'demo_user': os.getenv('demo_user', default='demo@billy.com'),
        'demo_user_password': os.getenv('demo_user_password', default='demo@123456'),
    })
    LOGGER.debug('Configuration is:')
    for config_name in _config.keys():
        if 'password' not in config_name:
            LOGGER.debug(f'{config_name}={_config[config_name]}')
    # LOGGER.setLevel(_config['log_level'])
    return _config


CONFIG = get_config()
