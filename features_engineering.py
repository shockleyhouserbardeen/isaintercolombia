import pandas as pd
#import matplotlib.pyplot as plt
#import seaborn as sns
#import folium
#from folium.plugins import HeatMap
#from IPython.display import display
#from folium.plugins import TimeSliderChoropleth
import haversine as hs
import numpy as np
from sqlalchemy import *

# Crear Engine para que pandas sepa a donde esta la data

#Aplicar en este orden, cada función devuelve otra tabla para aplicar a la siguiente

#### Funciones de ejecucion

#1. Calcula la columna de diferencia de tiempo entre la falla y la descarga
def diferencia_tiempo(df_rayos):
        
    df_rayos["Diff"]=""

    for idx,rayo_iter in df_rayos.iterrows():
        diff=(rayo_iter.loc["Fecha_Descarga"]-rayo_iter.loc["Fecha_Falla"]).total_seconds()
        
        df_rayos.loc[idx,"Diff"] = diff
        df_rayos["Diff"]=pd.to_numeric(df_rayos["Diff"])
    
    return df_rayos


#2. Devuelve la matriz de distancias de cada rayo con cada torre
def distancias_hav(rayos,torres):
    lista_de_listas=[]  
    list_of_indexes=[]
    for idx, rayo in rayos.iterrows():
        list_of_indexes.append(idx)
        #print(idx)       
        lista_de_rayos_torre=[]  

        for _,torre in torres.iterrows():
            
            distance_to_tower=hs.haversine((rayo["Latitud"],rayo["Longitud"]),(torre["Latitud"],torre["Longitud"]), "km")
            lista_de_rayos_torre.append(distance_to_tower) 

        lista_de_listas.append(lista_de_rayos_torre)
        
    df_distancias=pd.DataFrame(lista_de_listas, index=list_of_indexes)
    df_distancias.index.name="ID de Rayo"
    df_distancias=df_distancias.rename_axis("ID de Torre",axis=1)
            
    return(df_distancias)


#3. Crea columna con etiqueta de mayor y menor
def mayor_menor(rayos,df_distancias,valor):
    rayos["Rango de 5km"]=""
    for idx,torre in df_distancias.iterrows():

        if any(value<valor for value in torre):
            rayos.loc[idx,"Rango de 5km"]="Menor"
        else:
            rayos.loc[idx,"Rango de 5km"]="Mayor"
            
    return(rayos)

## 4.Filtrar por tiempo menor a -3600 y distancia "Menor" y organizar en la tabla semi-final
## merge entre tabla original y descriptiva de distancias

def filtros_distancia_tiempo(df_total,df_distancias,valor):
    df_total2=df_total[df_total["Rango de 5km"]=="Menor"]
    df_distancias.mask((df_distancias>valor), inplace=True)
    describe=df_distancias.iloc[:,1:].apply(pd.Series.describe, axis=1).add_prefix('Distancia_')
    merged=pd.merge(df_total2,describe, left_index=True, right_index=True)  
        
    return(merged)

## 5. Agrupar por intervalos 
def organizar_intervalos(merged):
    
    final=merged.groupby(["Linea","Num_Falla",pd.cut(merged["Diff"], np.arange(-5400, 600, 300))]).agg({"Magnitud":["min","max","sum","count","mean"], "Distancia_count":["sum"],"Distancia_min":["min"], "Distancia_max":["min"],"Distancia_mean":["sum","mean"]}).reset_index()
    final.columns=final.columns.droplevel()
    final.columns=["Linea","Num_falla","Intervalo_tiempo","magnitud_min", "magnitud_max","magnitud_sum","magnitud_count",
                 "magnitud_mean","distancia_count_sum","distancia_min_min","distancia_max_min",
                "distancia_mean_sum","distancia_mean_mean"]  
    return(final)
    
# 6. Nuevas variables agrupadas por tiempos
    
def nuevas_variables(pruebas):
    
    #rangos de filas para hacer los calculos
    num_intervalos=len(pruebas["Intervalo_tiempo"].unique()) 
    
    i1=0
    i2=num_intervalos 
    
    for i in range(num_intervalos):
        ## minima Magnitud minima en los ultimos minutos
        pruebas.loc[i1:i2,'magnitud_min_ult10'] = pruebas.iloc[i1:i2,3].rolling(window=2,min_periods=1).min()
        pruebas.loc[i1:i2,'magnitud_min_ult15'] = pruebas.iloc[i1:i2,3].rolling(window=3,min_periods=1).min()
        pruebas.loc[i1:i2,'magnitud_min_ult30'] = pruebas.iloc[i1:i2,3].rolling(window=6,min_periods=1).min()

        ##max Magnitud_max en los ultimos minutos
        pruebas.loc[i1:i2,'magnitud_max_ult10'] = pruebas.iloc[i1:i2,4].rolling(window=2,min_periods=1).max()
        pruebas.loc[i1:i2,'magnitud_max_ult15'] = pruebas.iloc[i1:i2,4].rolling(window=3,min_periods=1).max()
        pruebas.loc[i1:i2,'magnitud_max_ult30'] = pruebas.iloc[i1:i2,4].rolling(window=6,min_periods=1).max()

        ##promedio Magnitud_sum en los ultimos minutos
        pruebas.loc[i1:i2,"avg_magnitud_sum_ult10"] = pruebas.iloc[i1:i2,5].rolling(window=2,min_periods=1).mean()
        pruebas.loc[i1:i2,'avg_magnitud_sum_ult15'] = pruebas.iloc[i1:i2,5].rolling(window=3,min_periods=1).mean()
        pruebas.loc[i1:i2,'avg_magnitud_sum_ult30'] = pruebas.iloc[i1:i2,5].rolling(window=6,min_periods=1).mean()

        ##suma Magnitud_sum en los ultimos minutos
        pruebas.loc[i1:i2,'sum_magnitud_sum_ult10'] = pruebas.iloc[i1:i2,5].rolling(window=2,min_periods=1).sum()
        pruebas.loc[i1:i2,'sum_magnitud_sum_ult15'] = pruebas.iloc[i1:i2,5].rolling(window=3,min_periods=1).sum()
        pruebas.loc[i1:i2,'sum_magnitud_sum_ult30'] = pruebas.iloc[i1:i2,5].rolling(window=6,min_periods=1).sum()

        ##suma Magnitud_count en los ultimos minutos
        pruebas.loc[i1:i2,'sum_magnitud_count_ult10'] = pruebas.iloc[i1:i2,6].rolling(window=2,min_periods=1).sum()
        pruebas.loc[i1:i2,'sum_magnitud_count_ult15'] = pruebas.iloc[i1:i2,6].rolling(window=3,min_periods=1).sum()
        pruebas.loc[i1:i2,'sum_magnitud_count_ult30'] = pruebas.iloc[i1:i2,6].rolling(window=6,min_periods=1).sum()

        ##promedio Magnitud_mean en los ultimos minutos
        pruebas.loc[i1:i2,'avg_magnitud_mean_ult10'] = pruebas.iloc[i1:i2,7].rolling(window=2,min_periods=1).mean()
        pruebas.loc[i1:i2,'avg_magnitud_mean_ult15'] = pruebas.iloc[i1:i2,7].rolling(window=3,min_periods=1).mean()
        pruebas.loc[i1:i2,'avg_magnitud_mean_ult30'] = pruebas.iloc[i1:i2,7].rolling(window=6,min_periods=1).mean()

        ##suma distancia_count_sum en los ultimos minutos
        pruebas.loc[i1:i2,'sum_distancia_count_sum_ult10'] = pruebas.iloc[i1:i2,8].rolling(window=2,min_periods=1).sum()
        pruebas.loc[i1:i2,'sum_distancia_count_sum_ult15'] = pruebas.iloc[i1:i2,8].rolling(window=3,min_periods=1).sum()
        pruebas.loc[i1:i2,'sum_distancia_count_sum_ult30'] = pruebas.iloc[i1:i2,8].rolling(window=6,min_periods=1).sum()

        ##min "distancia_min_min" en los ultimos minutos 
        pruebas.loc[i1:i2,'min_distancia_min_min_ult10'] = pruebas.iloc[i1:i2,9].rolling(window=2,min_periods=1).min()
        pruebas.loc[i1:i2,'min_distancia_min_min_ult15'] = pruebas.iloc[i1:i2,9].rolling(window=3,min_periods=1).min()
        pruebas.loc[i1:i2,'min_distancia_min_min_ult30'] = pruebas.iloc[i1:i2,9].rolling(window=6,min_periods=1).min()

        ##min "distancia_max_min" en los ultimos minutos 
        pruebas.loc[i1:i2,'min_distancia_max_min_ult10'] = pruebas.iloc[i1:i2,10].rolling(window=2,min_periods=1).min()
        pruebas.loc[i1:i2,'min_distancia_max_min_ult15'] = pruebas.iloc[i1:i2,10].rolling(window=3,min_periods=1).min()
        pruebas.loc[i1:i2,'min_distancia_max_min_ult30'] = pruebas.iloc[i1:i2,10].rolling(window=6,min_periods=1).min()

        ##sum "distancia_mean_sum" en los ultimos minutos 
        pruebas.loc[i1:i2,'sum_distancia_mean_sum_ult10'] = pruebas.iloc[i1:i2,11].rolling(window=2,min_periods=1).sum()
        pruebas.loc[i1:i2,'sum_distancia_mean_sum_ult15'] = pruebas.iloc[i1:i2,11].rolling(window=3,min_periods=1).sum()
        pruebas.loc[i1:i2,'sum_distancia_mean_sum_ult30'] = pruebas.iloc[i1:i2,11].rolling(window=6,min_periods=1).sum()

        ##mean "distancia_mean_mean" en los ultimos minutos 
        pruebas.loc[i1:i2,'mean_distancia_mean_mean_ult10'] = pruebas.iloc[i1:i2,12].rolling(window=2,min_periods=1).mean()
        pruebas.loc[i1:i2,'mean_distancia_mean_mean_ult15'] = pruebas.iloc[i1:i2,12].rolling(window=3,min_periods=1).mean()
        pruebas.loc[i1:i2,'mean_distancia_mean_mean_ult30'] = pruebas.iloc[i1:i2,12].rolling(window=6,min_periods=1).mean()
        
        #nuevas filas para calcular
        i1=i2
        i2=i2+num_intervalos
        
    return(pruebas)

#7. Ultimo filtro de intervalo de fechas, filtrar solo la ultima hora de datos después de haber calculado
def filtrar_fechas_final(pruebas,tiempo_maximo):
    #tiempo_maximo=solo valores multiplos de -300
    
    leng=len(pruebas["Intervalo_tiempo"].unique())-len(np.arange(tiempo_maximo, 600, 300))+1
    
    num_fallas=len(pruebas["Num_falla"].unique())
    i1=0
    i2=leng
    num_intervalos=len(pruebas["Intervalo_tiempo"].unique())
    list_of_indices=[]
    for i in range(num_fallas):
        list_of_indices=list_of_indices+list(range(i1,i2))
        
        i1=num_intervalos*(i+1)
        i2=i1+leng
        
    pruebas=pruebas[~pruebas.index.isin(list_of_indices)]   
    
    return (pruebas.reset_index(drop=True))