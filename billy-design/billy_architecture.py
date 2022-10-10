from diagrams import Cluster, Diagram
from diagrams.programming.framework import React
from diagrams.aws.network import CloudFront, Route53, APIGateway
from diagrams.aws.compute import Lambda
from diagrams.aws.security import Cognito
from diagrams.aws.storage import S3
from diagrams.aws.database import Dynamodb
from diagrams.aws.integration import SNS, SQS
from diagrams.aws.management import ParameterStore
with Diagram("Billy Architecture", show=True, filename='billy_architecture'):
    ui = React("UI")
    dns = Route53('https://www.billy.adolha.com')
    cloud_front = CloudFront('CDN')
    ui_bucket = S3('UI Bucket')
    data_bucket = S3('Data Bucket')
    dns >> cloud_front
    cloud_front >> ui_bucket
    ui >> dns
    cognito = Cognito('Auth')
    apigw = APIGateway('Billy API Gateway')
    parameter_store = ParameterStore('Config & Secrets')
    with Cluster('AWS Lambda'):
        billy_api_lambda = Lambda('Billy API Lambda')
        billy_data_lambda = Lambda('Billy Data Lambda')
    parameter_store >> billy_api_lambda
    parameter_store >> billy_data_lambda
    billy_api_lambda >> data_bucket
    billy_data_lambda >> data_bucket
    ddb = Dynamodb('DDB Table')
    billy_api_lambda >> ddb
    billy_data_lambda >> ddb
    with Cluster('Events'):
        sns = SNS('SNS Topic')
        sqs = SQS('SQS')
    billy_api_lambda >> sns
    sns >> sqs
    ddb >> sns

    sqs >> billy_data_lambda
    ui >> apigw
    apigw >> billy_api_lambda
    cognito >> apigw
    # with Cluster("Lorem Ipsum - Kube"):
    #     with Cluster("db") as cluster:
    #         db_books = PostgreSQL("books")
    #         db_auth = PostgreSQL("auth")
    #     net = Nginx("loremipsum.com")
    #     net >> kube_svc('books', 2, db_books)
    #     net >> kube_svc('auth', 2, db_auth)
    #     search_engine = Service("Search Engine")
    #     db_books - search_engine
    # ui >> net
