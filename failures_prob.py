#failures_prob
import pandas as pd
import numpy as np
import datetime
# Libraria para manejar sql en python
from sqlalchemy import *
import features_engineering

import joblib

from sklearn.metrics import roc_curve, auc
from sklearn.model_selection import StratifiedKFold

# Visualizar todas las filas y columnas con scroll
# pd.set_option('display.max_rows', None)
# pd.set_option('display.max_columns', None)
# pd.set_option('display.width', None)

# Crear Engine para que pandas sepa a donde esta la data

def save_uploaded_table(df,engine):
    ##### Reading Sample Data
    #df_prueba = pd.read_csv("descargas_sample.csv", index_col=False)
    df_prueba = df
    df_prueba =  df_prueba.drop('Unnamed: 0', axis=1)

    # Transform Dataframe
    df_prueba = df_prueba.rename(columns = {'Fecha':'Fecha_Descarga'})

    #df_prueba["Fecha_Falla"] = datetime.datetime.today()
    df_prueba["Fecha_Falla"] = '2018-04-25 02:47:00'

    df_prueba["Fecha_Descarga"] = df_prueba["Fecha_Descarga"].astype('datetime64[s]')
    df_prueba["Fecha_Falla"] = df_prueba["Fecha_Falla"].astype('datetime64[s]')

    df_prueba["Num_Falla"] = 1

    df_prueba["Linea"] = 0

    #### Apply Feature Engineeering Functiones

    df_prueba.to_sql("temp_data_descargas",engine, if_exists = 'replace',index=False)
  
    return True
    
def giveMeFeatures(engine):
    ######## Main ###########
    # Leer contenido de la tabla y ponerlo en un PD dataframe
    sqltext = """
                  SELECT * FROM temp_data_descargas
                  """
    df_primavera = pd.read_sql_query(sqltext, engine)
    sqltext = """
                  SELECT * FROM georef
                  """
    torres_primavera = pd.read_sql_query(sqltext, engine)
    #1
    df_columna_diff=features_engineering.diferencia_tiempo(df_primavera)
    #2 En esta función se imprime el id de cada rayo para saber el progreso del calculo
    df_distancias=features_engineering.distancias_hav(df_columna_diff,torres_primavera)
    #Aquí se debería guardar en nuevo csv
    #3
    df_mayor_menor_label=features_engineering.mayor_menor(df_columna_diff,df_distancias,5)
    #4
    merged=features_engineering.filtros_distancia_tiempo(df_mayor_menor_label,df_distancias,5)
    #5
    por_intervalos=features_engineering.organizar_intervalos(merged)
    #6
    matriz_semifinal=features_engineering.nuevas_variables(por_intervalos)
    #7
    matriz_final=features_engineering.filtrar_fechas_final(matriz_semifinal,-3600)
    # Nombre PD_dataframe, y entre comillas el nombre con el que va quedar en la DB
    matriz_final['Intervalo_tiempo'] = matriz_final['Intervalo_tiempo'].astype('str')
    #matriz_final['Linea'] = matriz_final['Linea'].astype('int')
    matriz_final.to_sql('matriz_modelo', engine, if_exists = 'replace', index=False)
    return True

def run_model_probability(engine):
    ####### Calculate probability ###########
    sqltext = """
                SELECT * FROM matriz_modelo
                """
    matriz_final = pd.read_sql_query(sqltext, engine)

    Nan_dtc=['magnitud_min',
           'magnitud_max', 'magnitud_sum', 'magnitud_count', 'magnitud_mean',
           'distancia_count_sum', 'distancia_min_min', 'distancia_max_min',
           'distancia_mean_sum', 'distancia_mean_mean', 'magnitud_min_ult10',
           'magnitud_min_ult15', 'magnitud_min_ult30', 'magnitud_max_ult10',
           'magnitud_max_ult15', 'magnitud_max_ult30', 'avg_magnitud_sum_ult10',
           'avg_magnitud_sum_ult15', 'avg_magnitud_sum_ult30',
           'sum_magnitud_sum_ult10', 'sum_magnitud_sum_ult15',
           'sum_magnitud_sum_ult30', 'sum_magnitud_count_ult10',
           'sum_magnitud_count_ult15', 'sum_magnitud_count_ult30',
           'avg_magnitud_mean_ult10', 'avg_magnitud_mean_ult15',
           'avg_magnitud_mean_ult30', 'sum_distancia_count_sum_ult10',
           'sum_distancia_count_sum_ult15', 'sum_distancia_count_sum_ult30',
           'min_distancia_min_min_ult10', 'min_distancia_min_min_ult15',
           'min_distancia_min_min_ult30', 'min_distancia_max_min_ult10',
           'min_distancia_max_min_ult15', 'min_distancia_max_min_ult30',
           'sum_distancia_mean_sum_ult10', 'sum_distancia_mean_sum_ult15',
           'sum_distancia_mean_sum_ult30', 'mean_distancia_mean_mean_ult10',
           'mean_distancia_mean_mean_ult15', 'mean_distancia_mean_mean_ult30']

    matriz_final = matriz_final.fillna(0)

    sqltext = """
                    SELECT * FROM matriz_model_falla_compiled
                    """
    matrizT = pd.read_sql_query(sqltext, engine)

    matriz_final['Linea'] = 0

    for j in range(len(Nan_dtc)):
        matriz_final[Nan_dtc[j]]=(matriz_final[Nan_dtc[j]]-matrizT[Nan_dtc[j]].mean())/matrizT[Nan_dtc[j]].std()

    import joblib

    from sklearn.metrics import roc_curve, auc
    from sklearn.model_selection import StratifiedKFold

    model = joblib.load('model_f.data')

    X = matriz_final[['Linea', 'magnitud_min', 'magnitud_max', 'magnitud_sum',
           'magnitud_count', 'magnitud_mean', 'distancia_count_sum',
           'distancia_min_min', 'distancia_max_min', 'distancia_mean_sum',
           'distancia_mean_mean', 'magnitud_min_ult10', 'magnitud_min_ult15',
           'magnitud_min_ult30', 'magnitud_max_ult10', 'magnitud_max_ult15',
           'magnitud_max_ult30', 'avg_magnitud_sum_ult10',
           'avg_magnitud_sum_ult15', 'avg_magnitud_sum_ult30',
           'sum_magnitud_sum_ult10', 'sum_magnitud_sum_ult15',
           'sum_magnitud_sum_ult30', 'sum_magnitud_count_ult10',
           'sum_magnitud_count_ult15', 'sum_magnitud_count_ult30',
           'avg_magnitud_mean_ult10', 'avg_magnitud_mean_ult15',
           'avg_magnitud_mean_ult30', 'sum_distancia_count_sum_ult10',
           'sum_distancia_count_sum_ult15', 'sum_distancia_count_sum_ult30',
           'min_distancia_min_min_ult10', 'min_distancia_min_min_ult15',
           'min_distancia_min_min_ult30', 'min_distancia_max_min_ult10',
           'min_distancia_max_min_ult15', 'min_distancia_max_min_ult30',
           'sum_distancia_mean_sum_ult10', 'sum_distancia_mean_sum_ult15',
           'sum_distancia_mean_sum_ult30', 'mean_distancia_mean_mean_ult10',
           'mean_distancia_mean_mean_ult15', 'mean_distancia_mean_mean_ult30']]

    prediccion_data = model.predict_proba(X)

    df_prob = pd.DataFrame(data=prediccion_data, columns=["probility_light", "prob_inv"])

    matriz_final['light_prob'] = df_prob['probility_light']

    probabilidad_falla = float(matriz_final[matriz_final["Intervalo_tiempo"] == "(-300, 0]"]["light_prob"])
    return probabilidad_falla
