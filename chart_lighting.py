# Librearias
#Import Libraries
import pandas as pd
import numpy as np
import datetime
import plotly.express as px

# Libraria para manejar sql en python
from sqlalchemy import *

# Visualizar todas las filas y columnas con scroll
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

# Crear Engine para que pandas sepa a donde esta la data

#engine = create_engine('postgresql://postgres:PredictMachine2002+@bootcamprds.cepqmu7xn7vp.us-east-#2.rds.amazonaws.com:5432/projectisa')

def create_charts(linea, engine):
    if linea==1:
        sqltext = """
                    select * from descargas_virginia_sancarlos
                    where "Fecha" > '2020-03-01 03:51:48.823'
                    """
        virginia_db = pd.read_sql_query(sqltext, engine)


        fig_vig = px.density_mapbox(virginia_db, lat='Latitud', lon='Longitud', z='Magnitud', radius=10, zoom=7,
                                center=dict(lat=5.5983, lon=-75.3498), mapbox_style="carto-positron",
                                hover_data={'Corriente': True, 'Latitud': True, 'Longitud' : True})
        return fig_vig
    
    elif linea==2:
        sqltext = """
                    select * from descargas_cerro_prima
                    where "Fecha" > '2020-03-01 03:51:48.823'
                    """
        cerro_db = pd.read_sql_query(sqltext, engine)
        fig_cerro = px.density_mapbox(cerro_db, lat='Latitud', lon='Longitud', z='Magnitud', radius=10, zoom=7,
                                center=dict(lat=7.0525, lon=-74.9195), mapbox_style="carto-positron",
                                hover_data={'Corriente': True, 'Latitud': True, 'Longitud' : True})
        return fig_cerro
    
    elif linea==3:
        sqltext = """
                    select * from comuneros
                    where "Fecha" > '2019-11-01 03:51:48.823'
                    """
        comuneros_db = pd.read_sql_query(sqltext, engine)
        fig_comuneros = px.density_mapbox(comuneros_db, lat='Latitud', lon='Longitud', z='Magnitud', radius=10, zoom=8,
                                center=dict(lat=6.7738, lon=-73.9714), mapbox_style="carto-positron",
                                hover_data={'Corriente': True, 'Latitud': True, 'Longitud' : True})
        return fig_comuneros
    
    else :
        return False