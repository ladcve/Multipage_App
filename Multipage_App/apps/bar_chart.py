import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Row import Row
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash_html_components.Br import Br
import plotly.graph_objects as go
import plotly.express as px
import plotly.express as px
import dash_table
import sqlite3
import json
import configparser
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
query = "SELECT NOMBRE FROM ITEMS WHERE ESTATUS=1 "
well_list =pd.read_sql(query, con)
well_list = well_list.sort_values('NOMBRE')['NOMBRE'].unique()

#Listado de query
pathway = './querys'
files = [f for f in listdir(pathway) if isfile(join(pathway, f))]

file_name = ''

layout = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.Row([
                    dbc.Col([
                        html.Label(['Consulta:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                            id='dpd-query-list-bar',
                            options=[
                                {'label': i, 'value': i} for i in files
                            ],
                            clearable=False,
                            multi=False,
                        ),
                    ], width={"size": 3, "offset": 0}),
                    dbc.Col([
                        html.Label(['Pozo:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                            id='dpd-well-list',
                            options=[{'label': i, 'value': i} for i in well_list],
                            clearable=False,
                            multi=True
                        ),
                    ], width={"size": 4, "offset": 0}),
                    dbc.Col([
                        html.Label(['Fecha: '],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.DatePickerRange(
                            id='dtp_fecha',
                            min_date_allowed= date(1995, 8, 5),
                            max_date_allowed=date.today(),
                            start_date = date.today()- timedelta(days=-7),
                            end_date=date.today(),
                            display_format='YYYY-MM-DD',
                            style={'backgroundColor':'white'},
                        )
                    ]),
                ]),
                html.Br(),
            ]),
        ], width={"size": 8, "offset": 0}),
        dbc.Col([
            dbc.Card([
                dbc.Row([
                    dbc.Col([
                        html.Br(),
                        dbc.Button("Mostrar Gráfico", id="btn_show_barchart", color="success", className="mr-3"),
                    ], width={"size": 1, "offset": 1}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button("Exportar Imagen", id="btn_export_img", color="warning", className="mr-3"),
                    ], width={"size": 1, "offset": 3}),
                ]),
                html.Br(),
            ]),
        ]),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.Row([
                    dbc.Col([
                        html.Label(['Nombre Archivo:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dbc.Input(id="inp-ruta-barchart", placeholder="Type something...", type="text", style={'backgroundColor':'white'}),
                    ], width={"size": 3, "offset": 1}),
                     dbc.Col([
                        html.Br(),
                        dcc.Upload(
                            dbc.Button("Cargar Template", n_clicks=0, color="warning", className="mr-3"),
                            id='btn_open_barchart',
                            multiple=False
                        ),
                    ], width={"size": 3, "offset": 0}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button("Grabar Template", id="btn_save_barchart", n_clicks=0, color="warning", className="mr-3"),
                        html.Div(id="save_message_barchart"),
                    ]),
                ]),
                html.Br(),
            ]),
        ], width={"size": 6, "offset": 0}),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.Label(['Gráfico de Barras'],style={'font-weight': 'bold', "text-align": "left"})),
                dbc.CardBody([
                    dbc.Spinner(
                        dcc.Graph(id='cht-bar-chart',style={"height": 600, "width":1000}),
                    ),
                ])
            ]),
        ], width=9),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.Label(['Opciones'],style={'font-weight': 'bold', "text-align": "left"})),
                dbc.CardBody([
                    html.Label(['Nombre del Gráfico'],style={'font-weight': 'bold', "text-align": "left"}),
                    dbc.Input(id="inp_barchart_name", placeholder="Type something...", type="text", style={'backgroundColor':'white'}),
                    html.Br(),
                    dcc.RadioItems(
                        id="rdi_staked_columns",
                        options=[
                            {'label': '  Columnas Apiladas', 'value': 'STC'},
                            {'label': '  Sin Apilar', 'value': 'MTC'},
                        ],
                        value='STC'
                    ),
                    html.Br(),
                    html.Label(['Datos:'],style={'font-weight': 'bold', "text-align": "left"}),
                    dcc.Dropdown(
                        id='dpd-column-list',
                        clearable=False,
                        multi=True
                    ),
                ])
            ]),
        ], width=3),
    ]),
])

@app.callback(
    Output('cht-bar-chart','figure'),
    [Input("btn_show_barchart", "n_clicks"),
     Input('dpd-query-list-bar', 'value'), 
     Input('dpd-well-list', 'value'),
     Input('dpd-column-list', 'value'),
     Input('dtp_fecha', 'start_date'),
     Input('dtp_fecha', 'end_date'),
     Input('inp_barchart_name', 'value'),
     Input('rdi_staked_columns', 'value')])
def update_bar_chart(n_clicks, file_name, well_name, columns_list, dtp_start_date, dtp_end_date, chart_title, staked_columns):

    data_results = pd.DataFrame()
    query= ''
    fecha_inicio = str(dtp_start_date)
    fecha_fin = str(dtp_end_date)
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    fig = {}
    if 'btn_show_barchart' in changed_id:
        con = sqlite3.connect(archivo)
        if file_name is not None:
            with open(os.path.join(QUERY_DIRECTORY, file_name)) as f:
                contenido = f.readlines()
            if contenido is not None:
                if fecha_inicio is not None:
                    for linea in contenido:
                        query =  linea + " WHERE date(FECHA)>='"+fecha_inicio+"' AND  date(FECHA)<='"+fecha_fin+"' ORDER BY FECHA"
                else:
                    for linea in contenido:
                        query +=  linea 
                data_results =pd.read_sql(query, con)
                data_results =data_results.sort_values("FECHA")
                
                if well_name is not None and columns_list:
                    data_results= data_results[data_results['NOMBRE'].isin(well_name)]
                    if staked_columns=='STC':
                        fig = px.bar(data_results, x="NOMBRE", y=columns_list, title=chart_title, animation_frame="FECHA", animation_group="NOMBRE")
                    else:
                        fig = px.bar(data_results, x="NOMBRE", y=columns_list, title=chart_title,  barmode="group",animation_frame="FECHA", animation_group="NOMBRE")
    return fig

@app.callback(
    Output('dpd-column-list','options'),
    [Input('dpd-query-list-bar', 'value')])
def update_column_list(file_name):

    data_results = pd.DataFrame()
    columns = [{'label': i, 'value': i} for i in []]
    quer= ''
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'dpd-query-list' in changed_id:
        con = sqlite3.connect(archivo)
        if file_name:
            with open(os.path.join(QUERY_DIRECTORY, file_name)) as f:
                contenido = f.readlines()
                for linea in contenido:
                    query =  linea
                data_results =pd.read_sql(query, con)
                data_results =data_results.drop(['index', 'NOMBRE', 'FECHA'], axis=1)
                columns = [{'label': i, 'value': i} for i in data_results.columns]

    return columns

@app.callback(
    Output('save_message_barchart','children'),
    [Input('btn_save_barchart', 'n_clicks'),
    Input('dpd-query-list-bar', 'value'),
    Input('dpd-column-list', 'value'),
    Input('inp-ruta-barchart', 'value')]) 
def save_barchart(n_clicks, consulta, datos_y1, file_name ):
    mensaje=''
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'btn_save_linechart' in changed_id:
        data = {}
        data['grafico'] = []
        data['grafico'].append({
            'consulta': consulta,
            'datos_y1': datos_y1})
        if file_name:
            with open(CHART_DIRECTORY+file_name, 'w') as file:
                json.dump(data, file, indent=4)
            mensaje = 'Archivo guardado'
    return mensaje

@app.callback( [Output('inp-ruta-barchart', 'value'),
                Output('dpd-query-list-bar', 'value'),
                Output('dpd-column-list', 'value'),],
              [Input('btn_open_barchart', 'filename'),
              Input('btn_open_barchart', 'contents')]
              )
def open_barchart( list_of_names, list_of_contents):
    archivo = list_of_names
    consulta=[]
    datos_y1=[]

    if list_of_names is not None:
        print(list_of_names)
        archivo = list_of_names
        with open(CHART_DIRECTORY+archivo) as file:
            data = json.load(file)
            for drop_values   in data['grafico']:
                consulta = str(drop_values['consulta'])
                datos_y1 = drop_values['datos_y1']
    return archivo, consulta, datos_y1