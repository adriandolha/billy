from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

import boto3
from boto3.dynamodb.conditions import Key

from billy_data import LOGGER
from billy_data.config import get_config
from billy_data.app_context import app_context


class JobStatus(Enum):
    CREATED = "CREATED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


@dataclass
class Job:
    id: str
    created_at: datetime
    payload: str
    status: JobStatus
    completed_at: datetime = None
    result: str = None

    def to_dict(self):
        return {
            'id': self.id,
            'status': str(self.status.value),
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at and self.completed_at.isoformat(),
            'payload': self.payload,
            'result': self.result
        }

    @staticmethod
    def from_dict(data: dict) -> Job:
        return Job(id=data['id'],
                   status=JobStatus[data['status']],
                   payload=data['payload'],
                   created_at=datetime.fromisoformat(data.get('created_at')),
                   completed_at=datetime.fromisoformat(data.get('created_at')),
                   result=data.get('result'))

    def __eq__(self, other):
        return self.id == other.id if other else False


class JobService:
    def __init__(self):
        self.config = get_config()
        self.ddb = boto3.resource('dynamodb')
        self.table = self.ddb.Table(get_config()['ddb_table'])

    def get_all(self) -> list[Job]:
        username = app_context.username
        LOGGER.debug(f'Get all jobs for user {username}')
        response = self.table.query(KeyConditionExpression=Key('pk').eq(f'user#{username}')
                                                           & Key('sk').begins_with('job#')
                                    )
        LOGGER.debug(f'Get all jobs response: {response}')
        return [Job.from_dict(_job) for _job in response['Items']]

    def save(self, job: Job):
        item = {
            'pk': f'user#{app_context.username}',
            'sk': f'job#{job.id}',
            'lsi1_sk': f'status#{str(job.status.value)}',
            **job.to_dict()
        }
        LOGGER.debug(f'Adding job {item}')
        response = self.table.put_item(
            Item=item
        )
        LOGGER.debug(response)

        return job


job_service = JobService()
