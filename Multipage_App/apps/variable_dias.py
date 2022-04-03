import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Row import Row
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash_table.Format import Format, Symbol
import dash_admin_components as dac
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import dash_table
import sqlite3
import configparser
import sys
import os.path
import os
from os import listdir
from os.path import isfile, join
import numpy as np
import pandas as pd
import datetime
from collections import OrderedDict
import base64
import json
import os
import dash_daq as daq
from sklearn.preprocessing import PolynomialFeatures 
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline

#Variable con la ruta para salvar los querys
QUERY_DIRECTORY = "./querys"

#Lee el archivo de configuracion
configuracion = configparser.ConfigParser()

#Variable con la ruta para salvar los querys
QUERY_DIRECTORY = "./querys"
CHART_DIRECTORY = "./template/"

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
query = "SELECT * FROM CIERRE_DIARIO_POZO"
df =pd.read_sql(query, con)

df['DIAS']= (pd.to_datetime(df['FECHA'], format="%Y-%m-%d")-pd.to_datetime(df['FECHA'], format="%Y-%m-%d").min()).dt.days
#df['DIAS']=datetime.strptime(df['FECHA'], "%Y-%m-%d")
print(df)

