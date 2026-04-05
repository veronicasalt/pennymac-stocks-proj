import json
import os
import boto3
from decimal import Decimal


dynamodb = boto3.resource('dynamodb')

def handler(event, context):
    table_name = os.environ.get('TABLE_NAME')
    table = dynamodb.Table(table_name)

    try:
        response = table.scan(Limit=7)
        items = response.get('Items', [])

        return{
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS" 
            },
            "body": json.dumps(items)
        }
    except Exception as e:
        print(f"Error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Couldn't retrieve stock data"})
        }
    