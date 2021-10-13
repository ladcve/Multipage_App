import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Row import Row
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash_html_components.Br import Br
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
from datetime import date
from collections import OrderedDict
import base64
import os

from app import app 

#Variable con la ruta para salvar los querys
QUERY_DIRECTORY = "./querys"

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
query = "SELECT NOMBRE FROM ITEMS WHERE ESTATUS=1 "
well_list =pd.read_sql(query, con)
well_list = well_list.sort_values('NOMBRE')['NOMBRE'].unique()

#Listado de query
pathway = './querys'
files = [f for f in listdir(pathway) if isfile(join(pathway, f))]


layout = html.Div([
    dbc.Row([
        dbc.Col([
            html.Label(['Consulta:'],style={'font-weight': 'bold', "text-align": "left"}),
            
            dcc.Dropdown(
                id='dpd-query-list',
                options=[
                     {'label': i, 'value': i} for i in files
                 ],
                clearable=False
            ),
        ], width=2),
        dbc.Col([
            html.Label(['Pozo:'],style={'font-weight': 'bold', "text-align": "left"}),
            dcc.Dropdown(
                id='dpd-well-list',
                options=[{'label': i, 'value': i} for i in well_list],
                clearable=False
            ),
        ], width=1),
        dbc.Col([
            dbc.Button("Ejecutar Reporte", id="btn_execute_report", color="success", className="mr-3"),
        ], width=2),
        dbc.Col([
            dbc.Button("Exportar Excel", id="btn_export_excel", color="warning", className="mr-3"),
        ]),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.Label(['Reporte'],style={'font-weight': 'bold', "text-align": "left"})),
                dbc.CardBody([
                    dash_table.DataTable(
                        id='dt_report_results',
                        editable=False,
                        filter_action="native",
                        sort_action="native",
                        sort_mode="multi",
                        column_selectable="single",
                        row_selectable="multi",
                        row_deletable=False,
                        selected_columns=[],
                        selected_rows=[],
                        page_action="native",
                        page_current= 0,
                        page_size= 20,
                    ),
                ])
            ]),
        ], width=8),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.Label(['Opciones'],style={'font-weight': 'bold', "text-align": "left"})),
                dbc.CardBody([

                ])
            ]),
        ], width=4),
    ]),
])