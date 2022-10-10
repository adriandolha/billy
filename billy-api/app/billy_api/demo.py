import datetime
import json
import uuid
from typing import List
import boto3
from billy_api import LOGGER
from billy_api.auth import User, Groups, Group
from faker import Faker
from billy_api.cognito import CognitoClient
from billy_api.config import CONFIG
from billy_api.auth import auth_service
from billy_api.category import category_service, Category
from billy_api.app_context import app_context
import pandas as pd
from billy_api.repo import data_repo
from billy_api.job import job_service, Job, JobStatus
from billy_api.bank_statements import data_paths
import random
from faker import Faker


def configure_demo_user(email: str, password: str):
    cognito_client = CognitoClient()

    LOGGER.info('Running cognito setup...')
    demo_users_group = Groups.DEMO_USERS.value
    user_pool_id_ = CONFIG['cognito_user_pool_id']

    cognito_client.create_cognito_group(user_pool_id_, Groups.DEMO_USERS.value)
    username = cognito_client.create_cognito_user(email, user_pool_id_)
    response = cognito_client.add_user_to_group(email, user_pool_id_, demo_users_group)
    LOGGER.debug(response)
    cognito_client.confirm_user(email, password, user_pool_id_)
    demo_user = User(username, Groups.DEMO_USERS.value)
    app_context.username = username
    app_context.user = demo_user
    categories = category_service.load_from_file('categories.json')
    LOGGER.debug(categories)

    configure_user_categories(categories)
    configure_user_data(categories)
    if len(job_service.get_all()) == 0:
        add_test_jobs()


def add_test_jobs():
    job_service.save(
        Job(str(uuid.uuid4()), payload=json.dumps({'description': 'Just a simple test job for demo purposes.'}),
            job_type='test_job', created_at=datetime.datetime.now(), status=JobStatus.CREATED))
    job = Job(str(uuid.uuid4()), payload=json.dumps({'description': 'Just a simple test job for demo purposes.'}),
              job_type='test_job', created_at=datetime.datetime.now(), status=JobStatus.IN_PROGRESS)
    job.started_at = datetime.datetime.now()
    job_service.save(job)

    job = Job(str(uuid.uuid4()), payload=json.dumps({'description': 'Just a simple test job for demo purposes.'}),
              job_type='test_job', created_at=datetime.datetime.now(), status=JobStatus.COMPLETED)
    job.started_at = datetime.datetime.now()
    job.completed_at = datetime.datetime.now()
    job.result = json.dumps({'status': 'SUCCEEDED'})
    job_service.save(job)


def configure_user_categories(categories: List[Category]):
    for category in categories:
        category_service.save(category)


def update_bank_statement_data_metadata(last_updated):
    ddb = boto3.resource('dynamodb')
    username = app_context.username
    data_table = CONFIG['ddb_table']
    LOGGER.info(f'Update bank statement data last_updated at {last_updated}')
    response = ddb.Table(data_table).put_item(Item={
        'pk': f'user#{username}',
        'sk': 'bank_statement_data',
        'last_updated': str(last_updated)
    })
    LOGGER.debug(response)
    return last_updated


def get_all_dates_grouped_by_year_and_month(delta_days: int):
    today = datetime.datetime.today()
    dates_by_year_and_month = {}
    for days in range(0, delta_days):
        previous_date = today - datetime.timedelta(days=days)
        year_month = f'{previous_date.year}-{previous_date.month}'
        if not dates_by_year_and_month.get(year_month):
            dates_by_year_and_month[year_month] = []
        date = f'{year_month}-{previous_date.day}'
        dates_by_year_and_month[year_month].append(date)
    return dates_by_year_and_month


def configure_user_data(categories: List[Category]):
    _faker = Faker()
    category_names = [category.name for category in categories]
    LOGGER.debug(category_names)
    categories_by_name = {category.name: category.key_words for category in categories}
    data = []
    faker_config = {'food': {'suma_range': (-200, -50), 'entries_per_month': (20, 40)},
                    'transport': {'suma_range': (-250, -100), 'entries_per_month': (1, 3)},
                    'travel': {'suma_range': (-3000, -500), 'entries_per_month': (0, 1)},
                    'gas_electricity': {'suma_range': (-1000, -600), 'entries_per_month': (1, 1)},
                    'internet': {'suma_range': (-55, -30), 'entries_per_month': (1, 1)},
                    'phone': {'suma_range': (-300, -120), 'entries_per_month': (1, 1)},
                    'apartment': {'suma_range': (-800, -200), 'entries_per_month': (0, 1)},
                    'health': {'suma_range': (-200, -50), 'entries_per_month': (0, 3)}}
    dates = get_all_dates_grouped_by_year_and_month(365 * 3)
    for year_and_month in dates.keys():
        for category_name in faker_config.keys():
            # print(category_name)
            for i in range(0, random.randint(*faker_config[category_name]['entries_per_month'])):
                date = random.choice(dates[year_and_month])
                key_word = random.choice(categories_by_name[category_name])
                _text = _faker.text(max_nb_chars=random.randint(100, 300))
                desc = f'{key_word} {_text}'
                suma = random.randint(*faker_config[category_name]['suma_range'])
                data.append([date, desc, suma, category_name])

    data_file = data_paths(data_repo).all_data
    df = pd.DataFrame(columns=['date', 'desc', 'suma', 'category'], data=data)
    data_repo.save(data_file, bytes(df.to_json().encode('utf-8')))
    update_bank_statement_data_metadata(datetime.datetime.now())
