import boto3
import json
from datetime import datetime, timedelta

lambda_client = boto3.client('lambda', region_name='us-west-1') #

for i in range(1, 7):
    target_date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
    print(f"Triggering ingestor for {target_date}...")

    lambda_client.invoke(
        FunctionName='PennymacStocksProjStack-ingestor472414C8-KJIOydQAN6Pb',
        InvocationType='Event',
        Payload=json.dumps({"target_date": target_date})
    )