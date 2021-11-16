import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Row import Row
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash_html_components.Br import Br
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
from datetime import date
from collections import OrderedDict
import base64
import json
import os

from app import app 

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
query = "SELECT NOMBRE FROM ITEMS WHERE ESTATUS=1 "
well_list =pd.read_sql(query, con)
well_list = well_list.sort_values('NOMBRE')['NOMBRE'].unique()

con.close()

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
                            id='dpd-query-list',
                            options=[
                                {'label': i, 'value': i} for i in files
                            ],
                            clearable=False
                        ),
                    ], width={"size": 4, "offset": 1}),
                    dbc.Col([
                        html.Label(['Pozo:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                            id='dpd-well-list',
                            options=[{'label': i, 'value': i} for i in well_list],
                            clearable=False,
                            multi=False
                        ),
                    ], width={"size": 4, "offset": 0}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button("Mostrar Grafico", id="btn_show_chart", color="success", className="mr-3"),
                    ]),
                ]),
                html.Br(),
            ]),
        ], width={"size": 6, "offset": 0}),
        dbc.Col([
            dbc.Card([
                dbc.Row([
                    dbc.Col([
                        html.Label(['Nombre Archivo:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dbc.Input(id="inp-ruta-template", placeholder="Type something...", type="text", style={'backgroundColor':'white'}),
                    ], width={"size": 3, "offset": 1}),
                     dbc.Col([
                        html.Br(),
                        dcc.Upload(
                            html.Button('Cargar Archivo'),
                            id='btn_open_linechart',
                            multiple=False
                        ),
                    ], width={"size": 3, "offset": 0}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button("Grabar Template", id="btn_save_linechart", n_clicks=0, color="warning", className="mr-3"),
                        html.Div(id="save_message_report"),
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
                dbc.CardHeader(html.Label(['Gráfico de Scatter'],style={'font-weight': 'bold', "text-align": "left"})),
                dbc.CardBody([
                    dbc.Spinner(
                        dcc.Graph(id='cht-line-chart'),
                    ),
                ])
            ]),
        ], width=9),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.Label(['Opciones'],style={'font-weight': 'bold', "text-align": "left"})),
                dbc.CardBody([
                    dbc.Card([
                        dbc.CardHeader(html.Label(['Eje X'],style={'font-weight': 'bold', "text-align": "left"})),
                        dbc.CardBody([
                            html.Label(['Datos:'],style={'font-weight': 'bold', "text-align": "left"}),
                            dcc.Dropdown(
                                id='dpd-column-list-x',
                                clearable=False,
                                multi=False
                            ),
                        ]),
                    ]),
                    dbc.Card([
                        dbc.CardHeader(html.Label(['Eje Y'],style={'font-weight': 'bold', "text-align": "left"})),
                        dbc.CardBody([
                            html.Label(['Datos:'],style={'font-weight': 'bold', "text-align": "left"}),
                            dcc.Dropdown(
                                id='dpd-column-list-y',
                                clearable=False,
                                multi=False
                            ),
                        ]),
                    ]),
                    dbc.Card([
                        dbc.CardHeader(html.Label(['Eventos'],style={'font-weight': 'bold', "text-align": "left"})),
                        dbc.CardBody([
                            html.Br(),
                        ]),
                    ]),
                ])
            ]),
        ], width=3),
    ]),
])

@app.callback(
    Output('cht-line-chart','figure'),
    [Input("btn_show_chart", "n_clicks"),
     Input('dpd-query-list', 'value'), 
     Input('dpd-well-list', 'value'),
     Input('dpd-column-list-x', 'value'),
     Input('dpd-column-list-y', 'value')])
def update_line_chart(n_clicks, file_name, well_name, column_list_x, column_list_y):

    data_results = pd.DataFrame()
    query= ''
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    fig = {}
    
    if 'btn_show_chart' in changed_id:
        con = sqlite3.connect(archivo)
        if file_name is not None:
            with open(os.path.join(QUERY_DIRECTORY, file_name)) as f:
                contenido = f.readlines()
            if contenido is not None:
                if well_name is not None:
                    for linea in contenido:
                        query +=  linea 
                    data_results =pd.read_sql(query, con)
                    data_results =data_results.sort_values("FECHA")
                    data_results = data_results[data_results['NOMBRE']==well_name]
                    fig = px.scatter(x=data_results[column_list_x],
                            y=data_results[column_list_y],)
                    fig.update_layout(
                        autosize=False,
                        width=1000,
                        height=600,
                        margin=dict(
                            l=50,
                            r=50,
                            b=100,
                            t=100,
                            pad=4
                        ),
                    )
                    fig.update_layout(legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    ))
        con.close()
    return fig

@app.callback(
    [Output('dpd-column-list-x','options'),
     Output('dpd-column-list-y','options')],
    [Input('dpd-query-list', 'value')])
def update_column_list(file_name):

    data_results = pd.DataFrame()
    columns = [{'label': i, 'value': i} for i in []]
    query= ''
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'dpd-query-list' in changed_id:
        con = sqlite3.connect(archivo)
        if file_name:
            with open(os.path.join(QUERY_DIRECTORY, file_name)) as f:
                contenido = f.readlines()
                for linea in contenido:
                    query +=  linea
                data_results =pd.read_sql(query, con)
                columns = [{'label': i, 'value': i} for i in data_results.columns]
        con.close()

    return columns, columns

@app.callback(
    Output('save_message_report','children'),
    [Input('btn_save_linechart', 'n_clicks'),
    Input('dpd-query-list', 'value'),
    Input('dpd-column-list-x', 'value'),
    Input('dpd-column-list-y', 'value'),
    Input('inp-ruta-template', 'value')]) 
def save_chart(n_clicks, consulta, datos_y1, datos_y2, file_name ):
    mensaje=''
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'btn_save_linechart' in changed_id:
        data = {}
        data['grafico'] = []
        data['grafico'].append({
            'consulta': consulta,
            'datos_y1': datos_y1,
            'datos_y2': datos_y2})
        with open(CHART_DIRECTORY+file_name, 'w') as file:
            json.dump(data, file, indent=4)
        mensaje = 'Archivo guardado'
    return mensaje

@app.callback( [Output('inp-ruta-template', 'value'),
                Output('dpd-query-list', 'value'),
                Output('dpd-column-list-x', 'value'),
                Output('dpd-column-list-y', 'value'),],
              [Input('btn_open_linechart', 'filename'),
              Input('btn_open_linechart', 'contents')]
              )
def open_linechart( list_of_names, list_of_contents):
    archivo = list_of_names
    consulta=[]
    datos_y1=[]
    datos_y2=[]

    if list_of_names is not None:
        print(list_of_names)
        archivo = list_of_names
        with open(CHART_DIRECTORY+archivo) as file:
            data = json.load(file)
            for drop_values   in data['grafico']:
                consulta = str(drop_values['consulta'])
                datos_y1 = drop_values['datos_y1']
                datos_y2 = drop_values['datos_y2']
    return archivo, consulta, datos_y1, datos_y2