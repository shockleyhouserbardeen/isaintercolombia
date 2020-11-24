# Load packages

#import matplotlib.pyplot as plt
import numpy  as np
import pandas as pd
#import seaborn as sns
#import statsmodels.api as sm
#import statsmodels.formula.api as sfm
#from matplotlib.widgets import Slider, Button, RadioButtons
#from scipy import interp
#from scipy.optimize import fsolve
#from scipy.stats import chi2_contingency, ttest_ind
#from sklearn.metrics import roc_curve, auc
#from sklearn.model_selection import StratifiedKFold
#from statsmodels.formula.api import ols
#from IPython.display import display_html
#import datetime
from sqlalchemy import *
import joblib
import plotly.express as px


def lighting_probability_calculation():
    # Crear Engine para que pandas sepa a donde esta la data
    engine = create_engine('postgresql://postgres:PredictMachine2002+@bootcamprds.cepqmu7xn7vp.us-east-2.rds.amazonaws.com:5432/projectisa')

    # Load saved model
    model_xgb = joblib.load('model.data')

    # Leer contenido de la tabla y ponerlo en un PD dataframe
    sqltext = """
                    select max(time) as time from openweatherdatalive
                    where (forecast = 'a')
                    limit 1
                    """
    df_date = pd.read_sql_query(sqltext, engine)

    date_lastinput = df_date["time"][0]

    # Leer contenido de la tabla y ponerlo en un PD dataframe
    sqltext = f"""
                    select * from openweatherdatalive
                    where (forecast = 'a') and (time = '{date_lastinput}')
                    """
    weather_df = pd.read_sql_query(sqltext, engine)
    X = weather_df[['temp','pressure','humidity','wind_speed','wind_deg','clouds']].copy()
    X['Intercept'] = 1
    prediccion_data = model_xgb.predict_proba(X)
    df_prob = pd.DataFrame(data=prediccion_data, columns=["probility_light", "prob_inv"])
    weather_df['light_prob'] = (df_prob['probility_light']-0.9)*10
    weather_df.to_sql('lighting_weather_and_probability', engine, index=False, if_exists='replace')
    
    return weather_df


def chart_of_weather_probability(df):
    fig = px.density_mapbox(df, lat='latitude', lon='longitude', z='light_prob', radius=10, zoom=6,
                            center=dict(lat=6.49682, lon=-74.78966), mapbox_style="carto-positron",
                            hover_data={'main': True, 'temp': True, 'pressure': True, 'latitude': True, 'longitude' : True})
    return fig
    