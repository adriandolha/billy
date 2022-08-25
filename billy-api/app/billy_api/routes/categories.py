import json

from billy_api import LOGGER
from billy_api.auth import requires_permission, Permissions
from billy_api.category import category_service, Category


@requires_permission()
def get_all(event, context):
    categories = [job.to_dict() for job in category_service.get_all()]
    result = {'items': categories, 'total': len(categories)}
    return {
        "statusCode": 200,
        "body": json.dumps(result)
    }


# todo: add pydantid for validation
@requires_permission(Permissions.CATEGORY_ADD)
def save(event, context):
    body = json.loads(event.get('body'))
    LOGGER.info('Update category request...')
    LOGGER.debug(body)
    name = body.get('name')
    if not name:
        return {
            "statusCode": 400,
            "body": json.dumps('name required')
        }
    key_words = body.get('key_words')
    if not key_words:
        return {
            "statusCode": 400,
            "body": json.dumps('key_words required')
        }
    category = Category(name=name, key_words=key_words)
    category = category_service.save(category)
    return {
        "statusCode": 200,
        "body": json.dumps(category.to_dict())
    }
