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
query = "SELECT NOMBRE, FECHA, TASA_GAS FROM PRUEBAS_POZO"
data =pd.read_sql(query, con)
#print(data.groupby('NOMBRE')['PRESION_FONDO_A'].agg(['last']))
results = data[data['FECHA']<='2021-11-01 00:00:00']
print(results.groupby('NOMBRE').nth(-1))
