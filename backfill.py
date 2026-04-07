import boto3
import json
import time
from datetime import datetime, timedelta
from botocore.config import Config

custom_config = Config(read_timeout=150, connect_timeout=150, retries={'max_attempts': 2})
lambda_client = boto3.client('lambda', region_name='us-west-1', config=custom_config)
function_name = 'PennymacStocksProjStack-ingestor472414C8-KJIOydQAN6Pb'

# Official 2026 Holidays to skip
holidays = ["2026-04-03"]

def get_last_7_trading_days():
    days = []
    curr = datetime.now()
    while len(days) < 7:
        curr -= timedelta(days=1)
        d_str = curr.strftime('%Y-%m-%d')
        if curr.weekday() < 5 and d_str not in holidays:
            days.append(d_str)
    return days

for date in get_last_7_trading_days():
    print(f"Executing Ingestor for {date}...")
    try:
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps({"target_date": date})
        )
        # Parse the response to see what the Lambda actually found
        payload = json.loads(response['Payload'].read())
        print(f"Result for {date}: {payload.get('body', 'No body returned')}")
    except Exception as e:
        print(f"Failed {date}: {e}")
    
    # Increase wait to 30 seconds to be very safe with the API rate limits
    print("Waiting 30s to stay under API limits...")
    time.sleep(30)