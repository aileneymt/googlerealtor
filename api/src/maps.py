
from google.cloud import bigquery
import requests
import json
from google.auth import default
from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account
import os
from dotenv import load_dotenv
from google.oauth2 import service_account
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_KEY_FILE = os.getenv("SERVICE_KEY_FILE")
json_path = os.path.join(BASE_DIR, "..", SERVICE_KEY_FILE)
credentials = service_account.Credentials.from_service_account_file(
    json_path,
    scopes=["https://www.googleapis.com/auth/bigquery"]
)
print("Service account email:", credentials.service_account_email)

PROJECT_ID = os.getenv("PROJECT_ID")
client = bigquery.Client(credentials=credentials, project=PROJECT_ID)  # Your project ID


authed_session = AuthorizedSession(credentials)
creds, project = default()
print("Credentials:", creds)
print("Project:", project)

TABLE_NAME = f"{PROJECT_ID}.durham_county.available_listings"


def get_houses(price, bedrooms, bathrooms, city):
    query = ""
    if city:
        query =f"""
        SELECT * FROM {TABLE_NAME} 
        WHERE PRICE <= {price} AND BEDS >= {bedrooms} AND BATHS >= {bathrooms} AND CITY = "{city}"
        ORDER BY PRICE
        """
    else:
        query =f"""
        SELECT * FROM {TABLE_NAME} 
        WHERE PRICE <= {price} AND BEDS >= {bedrooms} AND BATHS >= {bathrooms} 
        ORDER BY PRICE
        """
    query_job = client.query(query)
    results = [dict(row) for row in query_job.result()]  # Convert rows to dictionaries
    return results

