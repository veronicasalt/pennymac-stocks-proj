import json
import os
import boto3
import time
from datetime import datetime, timedelta
from massive import RESTClient
from decimal import Decimal

def handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['TABLE_NAME'])
    api_key = os.environ.get('MASSIVE_API_KEY')
    client = RESTClient(api_key)

    stocks_list = [
            "AAPL",
            "MSFT",
            "GOOGL",
            "AMZN",
            "TSLA",
            "NVDA"
            ]
    
    results = []
    winner = None

    today = datetime.now()
    day_of_week = today.weekday()
    
    if day_of_week == 0: # Monday
        target_date = today - timedelta(days=3) # Friday
    elif day_of_week == 6: # Sunday
        target_date = today - timedelta(days=2) # Friday
    elif day_of_week == 5: # Saturday
        target_date = today - timedelta(days=1) # Friday
    else:
        target_date = today - timedelta(days=1) # in any case: get yesterday

    attempts = 0
    max_attempts = 5

    while attempts < max_attempts:
        date = target_date.strftime('%Y-%m-%d')
        print(f"Market data for: {date}")

        day_results = []

        for ticker in stocks_list:
            try:
                time.sleep(12)
                request = client.get_daily_open_close_agg(
                    ticker,
                    date
                )

                if hasattr(request, 'open') and request.open:
                    o = float(request.open)
                    c = float(request.close)
                    percent_change = ((c - o) / o) * 100
                    
                    day_results.append({
                        "Date": date,
                        "Ticker Symbol": ticker,
                        "Percent Change": Decimal(str(round(percent_change, 2))),
                        "Closing Price": Decimal(str(c)),
                    })
            except Exception as e:
                print(f"Error: no data for {ticker} on {date}: {e}")

        if day_results:
            results = day_results
            winner = max(results, key=lambda x: abs(x['Percent Change']))
            print(f"Winner on {date}: {winner['Ticker Symbol']}")
            break   
        else:
            print(f"No results found for {date}. Trying previous day:")
            target_date -= timedelta(days=1) 
            attempts += 1

    if winner:
        try:
            table.put_item(Item=winner)
            return {"statusCode": 200, "body": json.dumps(winner, default=str)}
        except Exception as e:
            print(f"DynamoDB Error: {e}")
            return {"statusCode": 500, "body": "Failed to save to database."}
    return {
        "statusCode": 404, "body": "No data found in window"}
