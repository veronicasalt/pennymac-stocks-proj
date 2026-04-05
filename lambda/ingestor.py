import json
import os
import boto3
import time
from datetime import datetime, timedelta
from massive import RESTClient

def handler(event, context):
    api_key = os.environ.get('MASSIVE_API_KEY')
    client = RESTClient(api_key)

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['TABLE_NAME'])

    if day_of_week == 0: # Monday
        target_date = today - timedelta(days=3) # Friday
    elif day_of_week == 6: # Sunday
        target_date = today - timedelta(days=2) # Friday
    elif day_of_week == 5: # Saturday
        target_date = today - timedelta(days=1) # Friday
    else:
        target_date = today - timedelta(days=1) # in any case: get yesterday

    date = str(target_date.date())
    print(f"Market data for: {date}")

    stocks_list = [
            "AAPL",
            "MSFT",
            "GOOGL",
            "AMZN",
            "TSLA",
            "NVDA"
            ]
    results = []


    for ticker in stocks_list:
        try:
            time.sleep(12)
            request = client.get_daily_open_close_agg(
                ticker,
                date,
                adjusted="true",
            )

            price_open = request.open
            price_close = request.close

            percent_change = ((price_close - price_open) / price_open) * 100
            results.append({
                "Date": date,
                "Ticker": ticker,
                "Change": percent_change,
                "Price": float(price_close),
            })
        except Exception as e:
            print(f"Error {ticker}: {e}")

    if not results:
        print("No results found.")
        return {"statusCode": 404, "body": "No data found."}
    
    winner = max(results, key=lambda x: abs(x['Change']))
    print(f"Winner found: {winner}")

    try:
        table.put_item(Item=winner)
        return {"statusCode": 200, "body": json.dumps(winner)}
    except Exception as e:
        print(f"DynamoDB Error: {e}")
        return {"statusCode": 500, "body": "Failed to save to database."}
