import logging
import os

logging.basicConfig(format='%(name)s %(asctime)s.%(msecs)03dZ %(levelname)s:%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logging.getLogger('faker').setLevel(logging.ERROR)
logging.getLogger('boto3.resources').setLevel(logging.ERROR)
logging.getLogger('urllib3.connectionpool').setLevel(logging.ERROR)
logging.getLogger('botocore.hooks').setLevel(logging.ERROR)
logging.getLogger('boto3.resources.action').setLevel(logging.ERROR)
logging.getLogger('boto3.resources.factory').setLevel(logging.ERROR)
logging.getLogger('botocore.auth').setLevel(logging.ERROR)
logging.getLogger('botocore.parsers').setLevel(logging.ERROR)
logging.getLogger('botocore.client').setLevel(logging.ERROR)
logging.getLogger('botocore.credentials').setLevel(logging.ERROR)
logging.getLogger('botocore.endpoint').setLevel(logging.ERROR)
logging.getLogger('botocore.httpsession').setLevel(logging.ERROR)
logging.getLogger('botocore.loaders').setLevel(logging.ERROR)

LOGGER = logging.getLogger('billy')
LOGGER.setLevel(os.getenv('log_level',default='ERROR'))

