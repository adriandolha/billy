import os
from functools import lru_cache
import boto3

ssm = boto3.client('ssm')


def load_config_from_ssm():
    env = 'prod'
    print('Loading config from SSM...')
    ssm_parameters = {
        'api_url': f'/{env}/api_url',
        'data_bucket': f'/{env}/data_bucket',
        'data_table': f'/{env}/data_table',
        'sns_topic_arn': f'/{env}/sns_topic_arn',
        'cognito_user_pool_id': f'/{env}/cognito_user_pool_id',
        'region': f'/{env}/region',
        'cognito_pool_domain': f'/{env}/cognito_domain',
        'cognito_client_id': f'/{env}/cognito_client_id',
        'cognito_user': f'/{env}/cognito_user',
        'cognito_redirect_uri': f'/{env}/cognito_redirect_uri',
        'cognito_user_password': f'/{env}/cognito_user_password'
    }
    for env_var_name, ssm_parameter in ssm_parameters.items():
        print(ssm_parameter)
        ssm_parameter_value = ssm.get_parameter(Name=ssm_parameter, WithDecryption=False)
        # print(ssm_parameter_value)
        os.environ[env_var_name] = ssm_parameter_value['Parameter']['Value']


@lru_cache()
def load_config():
    import json
    config_file = f"{os.path.expanduser('~')}/.cloud-projects/billy-local-integration.json"
    print(f'Config file is {config_file}')
    if os.path.exists(config_file):
        with open(config_file, "r") as _file:
            _config = dict(json.load(_file))
            for k, v in _config.items():
                os.environ[k] = str(v)
    else:
        load_config_from_ssm()
        _config = os.environ
    os.environ['prometheus_metrics'] = 'False'
    print('Config...')
    print(_config)
    return _config


load_config()
