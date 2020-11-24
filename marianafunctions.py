from datetime import datetime
import numpy as np
import pandas as pd

def add_descriptionscale(df):
   #df['dt']=df['dt'].apply(lambda x: datetime.fromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'))
   descrip=['very heavy rain', 'heavy intensity rain', 'moderate rain', 'light rain',        'overcast clouds', 'broken clouds', 'scattered clouds', 'few clouds','clear sky']
   color=list(np.arange(1,10,1))

   Aux1=[]

   for i in range(len(df['description'])):
     aux= color[descrip.index(df.description[i])]
     Aux1.append(aux)

   df['Description']=Aux1
    
   return df


def salidas_linea(fallas):
    fechas=fallas['Num_Falla'].unique()
    fechas=list(fechas)
    salidas =['Salida1', 'Salida2', 'Salida3', 'Salida4', 'Salida5', 'Salida6', 'Salida7', 'Salida8', 'Salida9', 'Salida10', 'Salida11', 'Salida12']
    
    def sal1(t1):
      aux1 = salidas[fechas.index(t1)]
      return aux1

    fallas['Salida']= fallas['Num_Falla'].apply(sal1)
    
    return fallas