import sqlite3
import configparser
import sys
import os.path
import os
import numpy as np
import pandas as pd
from datetime import date
from collections import OrderedDict
import base64
import os
from io import StringIO
import contextlib

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
query = "SELECT * FROM  CIERRE_DIARIO_POZO "
df =pd.read_sql(query, con)
query = "SELECT * FROM  VARIABLES "
variables =pd.read_sql(query, con)

selec_var=variables.loc[variables['NOMBRE']=='LIQ']

ecuacion = selec_var.iloc[0]['ECUACION']
titulo = selec_var.iloc[0]['TITULO']
evalu = eval(ecuacion)
df[titulo] = evalu
print(df)

@contextlib.contextmanager
def stdoutIO(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old

with stdoutIO() as s:
    eval("print(10+10)")

print("out:", s.getvalue())
