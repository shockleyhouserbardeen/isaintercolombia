from datetime import datetime as dt

import pandas as pd
from datetime import datetime
import math
import dash_html_components as html
import dash_table
import base64
import io

from sqlalchemy import *

def callWeather(engine):
  sqltext = """
                  SELECT * FROM openweatherdatalive_a
                  WHERE forecast = 'a'
                  """
  df = pd.read_sql_query(sqltext, engine)
  #df['dt'] = df['dt'].apply(lambda x : datetime.fromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'))
  #geoTemp.drop(columns=['index'], inplace=True)
  #print(df.shape)
  #print(df.head())

  return df

def callBase(db, engine):
  '''
  Request for info
  '''
  print('entré')
  sqltext = f"""
                SELECT * FROM {db}
                """
  df = pd.read_sql_query(sqltext, engine)
  df.drop(columns=['index'], inplace=True)
  print(df.shape)
  print(df.head())

  return df

def parse_contents(contents, filename, date):
  content_type, content_string = contents.split(',')

  decoded = base64.b64decode(content_string)
  try:
    if 'csv' in filename:
      # Assume that the user uploaded a CSV file
      df = pd.read_csv(
        io.StringIO(decoded.decode('utf-8')))
    elif 'xls' in filename:
      # Assume that the user uploaded an excel file
      df = pd.read_excel(io.BytesIO(decoded))
  except Exception as e:
    print(e)
    return html.Div([
      'There was an error processing this file.'
    ])
  
  return html.Div([
    html.H5(filename),
    html.H6(datetime.fromtimestamp(date)),

    dash_table.DataTable(
      data=df.to_dict('records'),
      columns=[{'name': i, 'id': i} for i in df.columns]
    ),

    html.Hr(),  # horizontal line

    # For debugging, display the raw contents provided by the web browser
    html.Div('Raw Content'),
    html.Pre(contents[0:200] + '...', style={
      'whiteSpace': 'pre-wrap',
      'wordBreak': 'break-all'
    })
  ])

def transformData(df, df2):
  df['Date'] = pd.to_datetime(df['Date'])
  dfNew = pd.merge(df, df2, left_on='OriginalLat', right_on='Latitud')

  dfNew['T2MMEAN_C'] = dfNew['T2MMEAN_K'] - 273.15
  dfNew['T2MMAX_C'] = dfNew['T2MMAX_K'] - 273.15
  dfNew['T2MMIN_C'] = dfNew['T2MMIN_K'] - 273.15

  #dfNew['air_temperature_10_C'] = dfNew['air_temperature_10'] - 273.15
  #dfNew['air_temperature_2_C'] = dfNew['air_temperature_2'] - 273.15
  #dfNew['tropopause_temperature_C'] = dfNew['tropopause_temperature'] - 273.15
  #dfNew['surface_skin_temperature_C'] = dfNew['surface_skin_temperature'] - 273.15

  return dfNew
