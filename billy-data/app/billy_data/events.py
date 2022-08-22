import dataclasses
import json
from enum import Enum

from billy_data import LOGGER
from billy_data.config import CONFIG

import boto3

sns = boto3.resource('sns')
SNS_TOPIC = CONFIG['sns_topic']
topic = sns.Topic(SNS_TOPIC)


class Events(Enum):
    JOB_CREATED = 'job.created'


@dataclasses.dataclass
class Event:
    name: str
    payload: str


def publish(event: Event):
    LOGGER.info(f'Publishing new event {event.name} to topic {SNS_TOPIC}...')
    LOGGER.debug(event)

    response = topic.publish(
        Message=json.dumps({'default': event.payload}),
        Subject='application event',
        MessageStructure='json',
        MessageAttributes={
            'event_name': {
                'DataType': 'String',
                'StringValue': event.name
            }
        }
    )
    LOGGER.debug(response)
    LOGGER.info(f'Published event {event.name}...')
    return response