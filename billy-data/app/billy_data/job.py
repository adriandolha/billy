from __future__ import annotations

import json
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
            'job_status': str(self.status.value),
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at and self.completed_at.isoformat(),
            'payload': self.payload,
            'job_result': self.result
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    @staticmethod
    def from_dict(data: dict) -> Job:
        return Job(id=data['id'],
                   status=JobStatus[data['job_status']],
                   payload=data['payload'],
                   created_at=datetime.fromisoformat(data.get('created_at')),
                   completed_at=datetime.fromisoformat(data.get('created_at')),
                   result=data.get('job_result'))

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

    def get(self, job_id: str) -> Job:
        username = app_context.username
        LOGGER.info(f'Get job {job_id}')
        response = self.table.query(KeyConditionExpression=Key('pk').eq(f'user#{username}')
                                                           & Key('sk').eq(f'job#{job_id}')
                                    )
        LOGGER.debug(f'Get job response: {response}')
        return [Job.from_dict(_job) for _job in response['Items']][0] if len(response['Items']) > 0 else None

    def save(self, job: Job):
        job_dict = job.to_dict()
        _pk = f'user#{app_context.username}'
        _sk = f'job#{job.id}'
        if not self.get(job.id):
            item = {
                'pk': _pk,
                'sk': _sk,
                'lsi1_sk': f'status#{str(job.status.value)}',
                **job_dict
            }
            LOGGER.debug(f'Adding job {item}')
            response = self.table.put_item(
                Item=item
            )
        else:
            update_expression = "set payload=:payload, " \
                      "completed_at=:completed_at, " \
                      "created_at=:created_at, " \
                      "job_status=:job_status, " \
                      "job_result=:job_result "
            print(update_expression)
            response = self.table.update_item(
                Key={'pk': _pk,
                     'sk': _sk},
                UpdateExpression=update_expression,
                ExpressionAttributeValues={
                    ':payload': job_dict['payload'],
                    ':completed_at': job_dict['completed_at'],
                    ':created_at': job_dict['created_at'],
                    ':job_status': job_dict['job_status'],
                    ':job_result': job_dict['job_result']
                }
            )

        LOGGER.debug(response)

        return job


job_service = JobService()
