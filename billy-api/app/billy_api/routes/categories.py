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


@requires_permission(Permissions.CATEGORY_UPDATE)
def update(event, context):
    name = event["pathParameters"]['category_name']

    body = json.loads(event.get('body'))
    if not (name == body.get('name')):
        return {
            "statusCode": 400,
            "body": json.dumps(f'path name {name} must be same as body name {body.get("name")} ')
        }

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


@requires_permission(Permissions.CATEGORY_DELETE)
def delete(event, context):
    name = event["pathParameters"]['category_name']
    LOGGER.info(f'Delete category {name} request...')
    category_service.delete(name)
    return {
        "statusCode": 204,
        "body": json.dumps('ok')
    }
