import json
import os
import boto3
from decimal import Decimal


dynamodb = boto3.resource('dynamodb')

def handler(event, context):
    table_name = os.environ.get('TABLE_NAME')
    table = dynamodb.Table(table_name)

    try:
        response = table.scan()
        items = response.get('Items', [])

        items.sort(key=lambda z: z['Date'], reverse=True) # newest items first
        recent_items = items[:7] ############### 7 or 6??
        return{
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS" 
            },
            "body": json.dumps(recent_items, default=str)
        }
    except Exception as e:
        print(f"Error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Couldn't retrieve stock data"})
        }
    