import pandas as pd
import stumpy
import numpy as np
import numpy.testing as npt
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import sqlite3
import configparser
import sys
import json
import os.path
import os
from os import listdir
from os.path import isfile, join
import numpy as np
import pandas as pd
from datetime import datetime, tzinfo, timezone, timedelta, date
from collections import OrderedDict
import base64
import os

#Variable con la ruta para salvar los querys
QUERY_DIRECTORY = "./querys"
TEMPLATE_DIRECTORY = "./template/"

#Lee el archivo de configuracion
configuracion = configparser.ConfigParser()

#Variable con la ruta para salvar los querys
QUERY_DIRECTORY = "./querys"

if os.path.isfile('config.ini'):

    configuracion.read('config.ini')

    if 'BasedeDatos' in configuracion:
        Origen = configuracion['BasedeDatos']['Origen']
        Catalogo = configuracion['BasedeDatos']['Catalogo']
        Password = configuracion['BasedeDatos']['Password']
        basededatos = configuracion['BasedeDatos']['Destino']
        ruta = configuracion['BasedeDatos']['ruta']

#Ruta de la BD
archivo = ruta +  basededatos
con = sqlite3.connect(archivo)

plt.rcParams["figure.figsize"] = [10, 6]  # width, height
plt.rcParams['xtick.direction'] = 'out'

#Listado de pozos activos
query = "SELECT FECHA, TASA_GAS FROM CIERRE_DIARIO_POZO WHERE NOMBRE='Perla-1X' AND  TASA_GAS>0"
T_df =pd.read_sql(query, con)
#T_df['FECHA'] = pd.to_datetime(T_df['FECHA'])

plt.suptitle('Pozo Perla-1X, T_df', fontsize='30')
plt.xlabel('Time', fontsize ='20')
plt.ylabel('TASA_GAS', fontsize='20')
plt.plot(T_df['TASA_GAS'])
plt.show()


Q_df= T_df[(T_df['FECHA'] >= '2020-07-05') & (T_df['FECHA'] <= '2020-08-26')]
print("Longitud Q_df:", len(Q_df))
print("Longitud T_df:", len(T_df))

plt.suptitle('Pozo Perla-1X, Q_df', fontsize='30')
plt.xlabel('Tiempo', fontsize ='20')
plt.ylabel('TASA_GAS', fontsize='20')
plt.plot(Q_df['TASA_GAS'])
plt.show()

distance_profile = stumpy.core.mass(Q_df["TASA_GAS"], T_df["TASA_GAS"])

# This simply returns the (sorted) positional indices of the top 16 smallest distances found in the distance_profile
k = 16
idxs = np.argpartition(distance_profile, k)[:k]
idxs = idxs[np.argsort(distance_profile[idxs])]

plt.suptitle('Sony AIBO Robot Dog Dataset, T_df', fontsize='30')
plt.xlabel('Tiempo', fontsize ='20')
plt.ylabel('TASA_GAS', fontsize='20')
plt.plot(T_df["TASA_GAS"])
for idx in idxs:
    print(idx)
    plt.plot(range(idx, idx+len(Q_df)), T_df["TASA_GAS"].values[idx:idx+len(Q_df)], lw=2)
plt.show()