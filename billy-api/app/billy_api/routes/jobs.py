import json
import uuid
from datetime import datetime

from billy_api import LOGGER
from billy_api.auth import requires_permission, Permissions
from billy_api.job import job_service, Job, JobStatus


@requires_permission()
def get_all(event, context):
    jobs = [job.to_dict() for job in job_service.get_all()]
    result = {'items': jobs, 'total': len(jobs)}
    return {
        "statusCode": 200,
        "body": json.dumps(result)
    }


@requires_permission(Permissions.JOB_ADD)
def save(event, context):
    body = json.loads(event.get('body'))
    LOGGER.info('Add job request...')
    LOGGER.debug(body)
    payload = body.get('payload')
    if not payload:
        return {
            "statusCode": 400,
            "body": json.dumps('payload required')
        }
    job = Job(id=str(uuid.uuid4()),
              created_at=datetime.now(),
              payload=payload,
              status=JobStatus.CREATED
              )
    job = job_service.save(job)
    return {
        "statusCode": 200,
        "body": json.dumps(job.to_dict())
    }
