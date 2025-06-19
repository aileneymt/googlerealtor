#Actual python stuff
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
import pickle
from xgboost import XGBRegressor
from sklearn.metrics import max_error
from sklearn import preprocessing, svm
from sklearn.metrics import root_mean_squared_error, mean_squared_error, mean_absolute_error, r2_score as r2
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import mean_absolute_percentage_error
from datetime import date
from enum import StrEnum
import io
from pmdarima.arima import auto_arima
import dataframe_image as dfi

#Get here the data cleaning stuff
from google.cloud import bigquery
import requests
import json
from google.auth import default
from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account
import os
from google.oauth2 import service_account
from flask import Flask, jsonify

VC = {27712: 29.4, 27703: 49.7, 27701: 70.2, 27707: 53.5, 27713: 39.5, 27704: 61.4, 27705: 47.4, 27503: 36.9, 27709: 23.4, 27278: 30.3}
PC = {27712: 40.8, 27703: 64.4, 27701: 78.2, 27707: 67.8, 27713: 58.3, 27704: 72.4, 27705: 63.7, 27503: 46.2, 27709: 31.9, 27278: 40}
  
#Basic setup stuff
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(BASE_DIR, "..", "rdu-sprinternship-2025-ee7f24ebcd45.json")
credentials = service_account.Credentials.from_service_account_file(
    json_path,
    scopes=["https://www.googleapis.com/auth/bigquery"]
)
print("Service account email:", credentials.service_account_email)

PROJECT_ID = "rdu-sprinternship-2025"
client = bigquery.Client(credentials=credentials, project='rdu-sprinternship-2025')  # Your project ID

authed_session = AuthorizedSession(credentials)
creds, project = default()
print("Credentials:", creds)
print("Project:", project)

#load pickle models
model = pickle.load(open('models/model.pkl', 'rb'))
model_27503 = pickle.load(open('models/27503.pkl', 'rb'))
model_27701 = pickle.load(open('models/27701.pkl', 'rb'))
model_27703 = pickle.load(open('models/27703.pkl', 'rb'))
model_27704 = pickle.load(open('models/27704.pkl', 'rb'))
model_27705 = pickle.load(open('models/27705.pkl', 'rb'))
model_27707 = pickle.load(open('models/27707.pkl', 'rb'))
model_27712 = pickle.load(open('models/27712.pkl', 'rb'))
model_27713 = pickle.load(open('models/27713.pkl', 'rb'))



class PropertyType(StrEnum):
  CONDO = "Condo/Co-op"
  MOBILE = "Mobile/Manufactured Home"
  SMALL_MF = "Multi-Family (2-4 Unit)"
  BIG_MF = "Multi-Family (5+ Unit)"
  RANCH = "Ranch"
  SF = "Single Family Residential"
  TOWNHOUSE = "Townhouse"



def load_data(beds, baths, square_feet, lot_size, year_built, property_type, latitude, longitude, zipcode, year, month):
  beds = float(beds)
  baths = float(baths)
  square_feet = float(square_feet)
  lot_size = float(lot_size)
  year_built = int(float(year_built))
  latitude = float(latitude)
  longitude = float(longitude)
  zipcode = int(float(zipcode))


  vc_rate = VC[int(zipcode)]
  pc_rate = PC[int(zipcode)]
  house_age = 2025 - year_built

  try:
    ptype = PropertyType(property_type)
  except ValueError:
    print("!!!!" + property_type)
    raise Exception("wrong property type")
  
  
  data = {'BEDS': [beds], 'BATHS': [baths], 'SQUARE FEET': [square_feet], 'LOT SIZE': [lot_size], 'YEAR BUILT': [year_built], 'LATITUDE': [latitude], 'LONGITUDE': [longitude], 
                'PROPERTY TYPE_Condo/Co-op': [0], 'PROPERTY TYPE_Mobile/Manufactured Home': [0], 'PROPERTY TYPE_Multi-Family (2-4 Unit)': [0], 
                'PROPERTY TYPE_Multi-Family (5+ Unit)': [0], 'PROPERTY TYPE_Ranch': [0], 'PROPERTY TYPE_Single Family Residential': [0], 'PROPERTY TYPE_Townhouse': [0],
                'PROPERTY_CRIME': [pc_rate], 'VIOLENT_CRIME': [vc_rate], 'YEAR': [year], 'MONTH': [month], 'HOUSE AGE': [house_age]}
  match ptype:
    case PropertyType.CONDO:
      data['PROPERTY TYPE_Condo/Co-op'][0] = 1
    case PropertyType.MOBILE:
      data['PROPERTY TYPE_Mobile/Manufactured Home'][0] = 1
    case PropertyType.SMALL_MF:
      data['PROPERTY TYPE_Multi-Family (2-4 Unit)'][0] = 1
    case PropertyType.BIG_MF:
      data['PROPERTY TYPE_Multi-Family (5+ Unit)'][0] = 1
    case PropertyType.RANCH:
      data['PROPERTY TYPE_Ranch'][0] = 1
    case PropertyType.SF:
      data['PROPERTY TYPE_Single Family Residential'][0] = 1
    case PropertyType.TOWNHOUSE:
      data['PROPERTY TYPE_Townhouse'][0] = 1
 
  try:
    df = pd.DataFrame(data)
  except Exception:
    raise Exception("creating df error")
  
  df.head(1)
  return df
  
#need a new prediction model that works better...
def prediction(data):
  temp = []
  try:
    for i in range(2020, 2025):
      data['YEAR'] = i
      temp.append(model.predict(data)[0])
  except Exception:
    raise Exception("fitting model error")
  return temp

def project(last_5, zipcode):
  map = {27503: model_27503, 27701: model_27701, 27703: model_27703, 27704: model_27704, 27705: model_27705, 27707: model_27707
         , 27712: model_27712, 27713: model_27713}
  time_model = map[zipcode]
  prediction = time_model.predict(n_periods = 61)

  temp = []
  temp.append(prediction.iloc[0])
  temp.append(prediction[12])
  temp.append(prediction[24])
  temp.append(prediction[36])
  temp.append(prediction[48])
  temp.append(prediction[60])

  ans = [last_5[-1]]
  for i in range(0, 5):
    ans.append((1 + (temp[i+1] - temp[i])/temp[i]) * ans[i])
  
    
  #Consider removing the 2025 predictions and only doing 2026...
  x_axis = np.arange(2020, 2031)
  
  fig, ax = plt.subplots(constrained_layout=True)
  ax.plot(x_axis, last_5 + ans, marker='o')


  #ax.set_yticks(ax.get_yticks())  # Keep default ticks
  ax.set_ylim(bottom=0) 
  ax.set_ylim(top = max(last_5 + ans) + 50000)
  ax.set_yticklabels([int(label / 1000) for label in ax.get_yticks()])

  plt.xlabel("Year")
  ax.set_ylabel("Price by $100k")

  plt.plot(x_axis, last_5 + ans)
  plt.grid()
  plt.title("Price vs Time Plot")

  buf = io.BytesIO()
  plt.savefig(buf, format='png')
  buf.seek(0)
  plt.close()

  return buf




def generate_plot(df):
  m1 = auto_arima(df['PRICE'], stepwise = True, error_action='ignore', seasonal=True, m=12)
  x_axis = np.arange(0, 5)
  df_2 = m1.predict(n_periods = 5)
  plt.plot(x_axis, df_2)
  plt.title("Price vs time Plot")

  #ax = fig.add_subplot(111)
  # ax.plot(x_axis, answer)
  # for xy in zip(x_axis, answer):
  # ax.annotate('(%s, %s)' % xy, xy=xy, textcoords='data')
  #ax.set_xlim(min(x_axis), max(x_axis))
  #ax.set_ylim(min(answer), max(answer))
  #ax.axis('off')

  buf = io.BytesIO()
  plt.savefig(buf, format='png')
  buf.seek(0)
  plt.close()

  return buf

def prediction(data):
  temp = []
  try:
    for i in range(2020, 2025):
      data['YEAR'] = i
      temp.append(model.predict(data)[0])
  except Exception:
    raise Exception("fitting model error")
  return temp

def project(last_5, zipcode):
  map = {27503: model_27503, 27701: model_27701, 27703: model_27703, 27704: model_27704, 27705: model_27705, 27707: model_27707
         , 27712: model_27712, 27713: model_27713}
  time_model = map[zipcode]
  prediction = time_model.predict(n_periods = 61)

  temp = []
  temp.append(prediction.iloc[0])
  temp.append(prediction[12])
  temp.append(prediction[24])
  temp.append(prediction[36])
  temp.append(prediction[48])
  temp.append(prediction[60])

  ans = [last_5[-1]]
  for i in range(0, 5):
    ans.append((1 + (temp[i+1] - temp[i])/temp[i]) * ans[i])
  
    
  #Consider removing the 2025 predictions and only doing 2026...
  x_axis = np.arange(2020, 2031)
  
  fig, ax = plt.subplots(constrained_layout=True)
  ax.plot(x_axis, last_5 + ans, marker='o')


  #ax.set_yticks(ax.get_yticks())  # Keep default ticks
  ax.set_ylim(bottom=0) 
  ax.set_ylim(top = max(last_5 + ans) + 50000)
  ax.set_yticklabels([int(label / 1000) for label in ax.get_yticks()])

  plt.xlabel("Year")
  ax.set_ylabel("Price by $100k")

  plt.plot(x_axis, last_5 + ans)
  plt.grid()
  plt.title("Price vs Time Plot")

  buf = io.BytesIO()
  plt.savefig(buf, format='png')
  buf.seek(0)
  plt.close()

  return buf
  

def prediction(data):
  temp = []
  try:
    for i in range(2020, 2025):
      data['YEAR'] = i
      temp.append(model.predict(data)[0])
  except Exception:
    raise Exception("fitting model error")
  return temp

def get_list(last_5, zipcode):
  map2 = {27503: model_27503, 27701: model_27701, 27703: model_27703, 27704: model_27704, 27705: model_27705, 27707: model_27707
         , 27712: model_27712, 27713: model_27713}
  time_model = map2[zipcode]
  prediction = time_model.predict(n_periods = 61)

  temp = []
  temp.append(round(prediction.iloc[0], 2))
  temp.append(round(prediction[12], 2))
  temp.append(round(prediction[24], 2))
  temp.append(round(prediction[36], 2))
  temp.append(round(prediction[48], 2))
  temp.append(round(prediction[60], 2))

  ans = [last_5[-1]]
  for i in range(0, 5):
    number = (1 + (temp[i+1] - temp[i])/temp[i]) * ans[i]
    ans.append(round(number, 2))
  
  fig, ax = plt.subplots()
  ax.axis('off')
  years = np.arange(2020, 2031)

  col_labels = list(map(str, years))
  
  cell_text = [["$" + str(temp)] for temp in(last_5 + ans)]
  #col_labels = list(map(str, (last_5 + ans)))

  table = ax.table(cellText=cell_text, rowLabels=col_labels, loc='center')

  table.auto_set_font_size(False)
  table.set_fontsize(16)
  table.scale(0.7, 2)
  plt.title("Price Over Time")
  
  buf = io.BytesIO()
  plt.savefig(buf, bbox_inches='tight', format='png')
  buf.seek(0)
  plt.close()

  return buf

  



  
  