import numpy as np
import numpy.random as rnd
import matplotlib.pyplot as plt 
import scipy.linalg as lin
import sqlite3
import configparser
import sys
import os.path
import pandas as pd
import os

#Lee el archivo de configuracion
configuracion = configparser.ConfigParser()

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

#Listado de pozos activos
query = "SELECT FECHA, PRESION_FONDO_A FROM LECTURAS_POZO WHERE NOMBRE='Perla-10'"
data =pd.read_sql(query, con)
print(data)

data.set_index('FECHA', inplace=True)
data.index = pd.to_datetime(data.index)
data = data.resample('1M').sum()

print(data)