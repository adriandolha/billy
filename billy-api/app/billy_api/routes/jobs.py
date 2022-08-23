import json

from billy_api.auth import requires_permission
from billy_api.job import job_service


@requires_permission()
def get_all(event, context):
    jobs = [job.to_dict() for job in job_service.get_all()]
    result = {'items': jobs, 'total': len(jobs)}
    return {
        "statusCode": 200,
        "body": json.dumps(result)
    }
