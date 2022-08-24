import json

from billy_api.auth import requires_permission
from billy_api.category import category_service


@requires_permission()
def get_all(event, context):
    categories = [job.to_dict() for job in category_service.get_all()]
    result = {'items': categories, 'total': len(categories)}
    return {
        "statusCode": 200,
        "body": json.dumps(result)
    }
