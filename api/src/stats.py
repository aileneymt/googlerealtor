import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from datetime import date
from google.cloud import bigquery
import requests
import json
from google.auth import default
from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account
import os
from dotenv import load_dotenv
from google.oauth2 import service_account
from flask import Flask, jsonify

import numpy as np
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(BASE_DIR, "..", "rdu-sprinternship-2025-ee7f24ebcd45.json")
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



def load_data(): 
  # 1. First get ALL date columns dynamically
  column_list_query = f"""
  SELECT column_name 
  FROM `{PROJECT_ID}.durham_county.INFORMATION_SCHEMA.COLUMNS`
  WHERE 
    table_name = 'zipcode_sales' AND
    REGEXP_CONTAINS(column_name, '^[0-9]{4}-[0-9]{2}-[0-9]{2}$')
  ORDER BY column_name
  """


  # Run the query
  column_query_job = client.query(column_list_query)
  date_columns = [row.column_name for row in column_query_job.result()]

  print(f"Date Columns: {date_columns}")

  # Build UNPIVOT clause safely
  unpivot_clause = ",\n    ".join([f"`{col}`" for col in date_columns])



  # 3. Main query with proper UNPIVOT syntax
  query = f"""
  SELECT
    RegionName AS zipcode,
    PARSE_DATE('%Y-%m-%d', date_col) AS observation_date,
    price,
    DATE_DIFF(PARSE_DATE('%Y-%m-%d', date_col), '2001-01-01', DAY) AS days_since_2001,
    EXTRACT(YEAR FROM PARSE_DATE('%Y-%m-%d', date_col)) AS year,
    EXTRACT(MONTH FROM PARSE_DATE('%Y-%m-%d', date_col)) AS month,
    SIN(2 * ACOS(-1) * EXTRACT(MONTH FROM PARSE_DATE('%Y-%m-%d', date_col))/12) AS month_sin,
    COS(2 * ACOS(-1) * EXTRACT(MONTH FROM PARSE_DATE('%Y-%m-%d', date_col))/12) AS month_cos
  FROM `{PROJECT_ID}.durham_county.zipcode_sales`
  UNPIVOT(
    price FOR date_col IN (
      {unpivot_clause}
    )
  )
  WHERE price IS NOT NULL AND
    PARSE_DATE('%Y-%m-%d', date_col) >= DATE_SUB(CURRENT_DATE(), INTERVAL 1 YEAR)
  ORDER BY zipcode, observation_date
  LIMIT 1000  # Remove this to get all results
  """


  query_job = client.query(query)
  results = query_job.result()

  df = pd.DataFrame([dict(row) for row in results])


  plt.figure(figsize=(12, 6))
  sns.lineplot(data=df, x='observation_date', y='price', hue='zipcode', marker='o', palette='tab10', alpha=0.7)

  plt.title("Sales Price Over Time")
  plt.xlabel("Observation Date")
  plt.ylabel("Price")
  plt.xticks(rotation=45)
  plt.grid(alpha=0.3)
  plt.tight_layout()
  plt.show()

  return df


def predict_and_plot_zipcode(df, zipcode, years):
    # Filter for the specified zipcode
    df_zip = df[df['zipcode'] == zipcode].copy()
    
    # Ensure data is sorted by date
    df_zip = df_zip.sort_values('observation_date')
    
    # Convert dates to ordinal
    df_zip['date_ordinal'] = pd.to_datetime(df_zip['observation_date']).map(pd.Timestamp.toordinal)
    
    # Features and target
    X = df_zip[['date_ordinal']]
    y = df_zip['price']
    
    # Check if there is enough data for the specified zipcode
    if len(X) < 2:
        print(f"Not enough data for zipcode {zipcode}.")
        return

    # Initialize and fit the model
    model = LinearRegression()
    model.fit(X, y)
    
    # Predict for the next year
    future_date = pd.Timestamp.now() + pd.DateOffset(years)
    future_ordinal = future_date.toordinal()
    future_price = model.predict([[future_ordinal]])[0]
    
    print(f"Predicted price for zipcode {zipcode} {years} year(s) from now: {future_price:.2f}")

    # Plotting
    plt.figure(figsize=(12, 6))
    plt.scatter(X, y, alpha=0.5, label="Actual Data")
    plt.plot(X, model.predict(X), color='red', label="Regression Line")
    plt.axvline(x=future_ordinal, color='blue', linestyle='--', label="1 Year from Now")
    plt.title(f"Linear Regression for Zipcode {zipcode}")
    plt.xlabel("Date (Ordinal)")
    plt.ylabel("Price")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()
    return future_price

# Example usage:
# Replace '12345' with an actual zipcode from your dataset
#df = load_data()
#predict_and_plot_zipcode(df, 27503, 1)
