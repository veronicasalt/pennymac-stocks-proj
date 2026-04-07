from aws_cdk import (
    Duration,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_events as events,
    aws_events_targets as targets, ############3
    aws_apigateway as apigw,
    aws_secretsmanager as secrets,
    aws_amplify_alpha as amplify,
    RemovalPolicy,
    Stack,
    SecretValue
    # aws_sqs as sqs,
)
from constructs import Construct

class PennymacStocksProjStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        stock_table = dynamodb.Table(
            self, "StockTable",
            partition_key=dynamodb.Attribute(
                name="Date",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="Ticker Symbol",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )   # dynamoDB
        
        # Secrets Manager 
        api_key_secret = secrets.Secret.from_secret_name_v2(self, "Massive Secret", "MassiveAPIKey")

        # Lambda functions
        ingestor_lambda = _lambda.Function(
            self, "ingestor",
            code=_lambda.Code.from_asset("lambda"),
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="ingestor.handler",
            memory_size=512,
            timeout=Duration.minutes(15),
            environment={
                "TABLE_NAME": stock_table.table_name,
                "MASSIVE_API_KEY": api_key_secret.secret_value.unsafe_unwrap()
            }
        )

        retriever_lambda = _lambda.Function(
            self, "retriever",
            code=_lambda.Code.from_asset("lambda"),
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="retriever.handler",
            timeout=Duration.seconds(30),
            environment ={
                "TABLE_NAME": stock_table.table_name
            }
        )

        # API Gateway #########
        api = apigw.LambdaRestApi(
            self, "StocksAPI",
            handler=retriever_lambda,
            proxy = False
        )
        movers = api.root.add_resource("movers")
        movers.add_method("GET")

        # EventBridge
        daily_rule = events.Rule(
            self, "DailyStockCheckRule",
            schedule=events.Schedule.cron(minute="23", hour="0")
        )
        daily_rule.add_target(targets.LambdaFunction(ingestor_lambda))

        # Grant permissions
        stock_table.grant_read_data(retriever_lambda)
        stock_table.grant_write_data(ingestor_lambda)
        api_key_secret.grant_read(ingestor_lambda)
    
        amplify_app = amplify.App(
            self, "StocksFrontend",
            source_code_provider=amplify.GitHubSourceCodeProvider(
                owner="veronicasalt",
                repository="pennymac-stocks-proj",
                oauth_token=SecretValue.secrets_manager("veronicasalt_fine_grain_token")
            ),
            environment_variables={
                "API_URL": api.url
            }
        )
        amplify_app.add_branch("main")
        
        # example resource
        # queue = sqs.Queue(
        #     self, "PennymacStocksProjQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )
