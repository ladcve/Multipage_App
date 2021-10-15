import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Row import Row
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash_html_components.Br import Br
import plotly.graph_objects as go
import plotly.express as px
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
                clearable=False,
                multi=True
            ),
        ], width=4),
        dbc.Col([
            html.Label(['Fecha: '],style={'font-weight': 'bold', "text-align": "left"}),
            dcc.DatePickerSingle(
                id='dtp_fecha',
                date=date.today(),
                display_format='YYYY-MM-DD',
                style={'backgroundColor':'white'},
            )
        ], width=2),
        dbc.Col([
            html.Br(),
            dbc.Button("Mostrar Grafico", id="btn_show_chart", color="success", className="mr-3"),
        ], width=1.5),
        dbc.Col([
            html.Br(),
            dbc.Button("Exportar Imagen", id="btn_export_img", color="warning", className="mr-3"),
        ]),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.Label(['Gráfico de Barras'],style={'font-weight': 'bold', "text-align": "left"})),
                dbc.CardBody([
                    dbc.Spinner(
                        dcc.Graph(id='cht-bar-chart'),
                    ),
                ])
            ]),
        ], width=9),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.Label(['Opciones'],style={'font-weight': 'bold', "text-align": "left"})),
                dbc.CardBody([
                    html.Label(['Nombre del Gráfico'],style={'font-weight': 'bold', "text-align": "left"}),
                    dbc.Input(id="inp_chart_name", placeholder="Type something...", type="text", style={'backgroundColor':'white'}),
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
    [Input("btn_show_chart", "n_clicks"),
     Input('dpd-query-list', 'value'), 
     Input('dpd-well-list', 'value'),
     Input('dpd-column-list', 'value'),
     Input('dtp_fecha', 'date'),
     Input('inp_chart_name', 'date'),
     Input('rdi_staked_columns', 'value')])
def update_bar_chart(n_clicks, file_name, well_name, columns_list, dtp_fecha, chart_title, staked_columns):

    data_results = pd.DataFrame()
    quer= ''
    fecha = str(dtp_fecha)
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    fig = go.Figure()
    if 'btn_show_chart' in changed_id:
        con = sqlite3.connect(archivo)
        if file_name is not None:
            with open(os.path.join(QUERY_DIRECTORY, file_name)) as f:
                contenido = f.readlines()
            if contenido is not None:
                if fecha is not None:
                    for linea in contenido:
                        query =  linea + " WHERE date(FECHA)='"+fecha+"' ORDER BY FECHA"
                else:
                    for linea in contenido:
                        query =  linea +" ORDER BY FECHA"
                data_results =pd.read_sql(query, con)
                if well_name is not None:
                    data_results= data_results[data_results['NOMBRE'].isin(well_name)]
                for columna in columns_list:
                    fig.add_trace(go.Bar(
                        x=data_results['NOMBRE'],
                        y=data_results[columna],
                        name=columna
                    ))
                if staked_columns=='STC':
                    fig.update_layout(barmode='stack', xaxis={'categoryorder':'category ascending'})
                fig.update_layout(title_text=chart_title)
                fig.update_layout(legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ))
    return fig

@app.callback(
    Output('dpd-column-list','options'),
    [Input('dpd-query-list', 'value')])
def update_column_list(file_name):

    data_results = pd.DataFrame()
    columns = [{'label': i, 'value': i} for i in []]
    quer= ''
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'dpd-query-list' in changed_id:
        con = sqlite3.connect(archivo)
        if file_name is not None:
            with open(os.path.join(QUERY_DIRECTORY, file_name)) as f:
                contenido = f.readlines()
                for linea in contenido:
                    query =  linea
                data_results =pd.read_sql(query, con)
                data_results =data_results.drop(['index', 'NOMBRE', 'FECHA'], axis=1)
                columns = [{'label': i, 'value': i} for i in data_results.columns]

    return columns