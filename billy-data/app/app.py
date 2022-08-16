import json

from billy_data import LOGGER


def lambda_handler(event, context):
    LOGGER.info(event)
    LOGGER.info(context)
    return {
        "statusCode": 200,
        "body": json.dumps('ok'),
    }

