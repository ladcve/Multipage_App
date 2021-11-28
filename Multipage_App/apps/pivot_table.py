import dash_pivottable
import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Row import Row
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
import dash_table
import sqlite3
import configparser
import json
import sys
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

from app import app 

#Variable con la ruta para salvar los querys
QUERY_DIRECTORY = "./querys"
CHART_DIRECTORY = "./template/"

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

#Listado de pozos activos
query = "SELECT * FROM CIERRE_DIARIO_POZO"
data =pd.read_sql(query, con)

content = html.Div(id="container3", children=[])

layout = html.Div([
    dash_pivottable.PivotTable(
        id='table',
        data=data,
        cols=['FECHA'],
        colOrder="key_a_to_z",
        rows=['NOMBRE'],
        rowOrder="key_a_to_z",
        rendererName="Grouped Column Chart",
        aggregatorName="Average",
        vals=["TASA_GAS"],
    ),
     html.Div(content),
])


@app.callback(Output('output', 'children'),
              [Input('table', 'cols'),
               Input('table', 'rows'),
               Input('table', 'rowOrder'),
               Input('table', 'colOrder'),
               Input('table', 'aggregatorName'),
               Input('table', 'rendererName')])
def display_props(cols, rows, row_order, col_order, aggregator, renderer):
    return [
        html.Div([
            html.P(str(cols), id='columns'),
            html.P(str(rows), id='rows'),
            html.P(str(row_order), id='row_order'),
            html.P(str(col_order), id='col_order'),
            html.P(str(aggregator), id='aggregator'),
            html.P(str(renderer), id='renderer'),
        ])
    ]
