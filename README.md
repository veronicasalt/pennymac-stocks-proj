# Stocks Serverless Pipeline
This project tracks a specific list of stocks, identifies the one with the highest absolute percent change in the market each day, and displays a 7-day history on a responsive web dashboard. 


**Stock Watchlist**: AAPL, MSFT, GOOGL, AMZN, TSLA, NVDA

## Architecture
The system is built entirely on AWS CDK (Infrastructure as Code), meaning the entire stack is defined in pennymac_stocks_proj_stack.py. This approach avoids manual configuration in AWS Console, which ensures reproducibility.


**Infrastructure**: AWS CDK (Python),


**Automation**: Amazon EventBridge, triggers a daily Cron job at 1:00 UTC (5:00pm PST),


**Compute**: Lambda functions (ingestor.py and retriever.py),


* ingestor.py: fetches data from Massive API, calculates the daily winner, and saves to DynamoDB.


* retriever.py: fetches the last 7 days of results with a TTL cache to optimize performance given high traffic or frequency of data fetching.


**Storage**: Amazon DynamoDB,


**API Layer**: Amazon API Gateway (REST),


**Frontend**: React hosted on AWS Amplify, Recharts for interactive data visualization,


**CI/CD**: Github Actions using OpenID Connect (OIDC)

## Deployment
### Prerequisites:
Massive API Key: Obtain a free key from Massive.com


GitHub Token: A fine-grained personal access token stored in Secrets Manager so Amplify can access and deploy the repository. Permissions: Contents read, Webhooks read/write


The AWS Toolkit Extension is helpful to have, but not required for this project.


Run this command to "log in" to your aws account, so your computer knows this AWS account to send code to: `aws configure`.

Install AWS CDK `npm install -g aws-cdk`


Make sure to install Node.js `npm install`
### Secret Storage: 
Store keys in AWS Secrets Manager to avoid coding or committing Access Keys of API Secrets. Use .gitignore! 

* Use this command to store your API Key: `aws secretsmanager create-secret --name MassiveAPIKey --secret-string Your_API_Key`
* Use this command to store your fine-grain token: `aws secretsmanager create-secret --name veronicasalt_fine_grain_token --secret-string Your_GitHub_Personal_Token`

### Backend Setup:
Clone the repository `python3 -m venv .env` and create a virtual environment.


Install dependencies `pip install -r requirements.txt`.

### Provisioning and Deploy: 
Boostrapping the environment is only necessary once,
`cdk bootstrap aws:://<account id>/us-west-1

However, if you don't have GitHub Actions set up, this command is necessary to deploy. Otherwise, everytime you commit and push code to your GitHub repository, it will be deployed to AWS as well.
`cdk deploy


## Challenges 
1. API Rate: The Massive API has a limit of 5 requests per minute. To prevent 429  errors, ingestor.py uses a throttling delay of time.sleep(12) between ticker requests (60 seconds / 5 requests = 12 seconds per request).


2. IAM: Encountered “Provisioning Missing Trust” errors when deploying the frontend. This was resolved after updating the IAM stack to use a Composite Principal- which allows Amplify and CodeBuild to hold IAM Service Roles.


3. Weekend and Holiday Gaps: The ingestor logic has to detect not just weekends, but holidays when the market is closed. To account for this, the logic uses a recursive lookback mechanism that checks previous days until it finds valid trading data.

## Dashboard
* A line chart shows the trend of daily winners for the past 7 days. Data points on the graph are automatically colored either Red or Green to mark whether it is a gain or a loss.
* Cards have stock information such as price data, percent change, and date. Cards are responsive after hovering over them. The layout is flexible to mobile and desktop screens.

Project Link: https://github.com/veronicasalt/pennymac-stocks-proj.git 


Live Demo: https://main.d1zvq0nkbapr6l.amplifyapp.com/
