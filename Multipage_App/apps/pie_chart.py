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

#Lista de colores
night_colors = ['rgb(56, 75, 126)', 'rgb(18, 36, 37)', 'rgb(34, 53, 101)',
                'rgb(36, 55, 57)', 'rgb(6, 4, 4)']
sunflowers_colors = ['rgb(177, 127, 38)', 'rgb(205, 152, 36)', 'rgb(99, 79, 37)',
                     'rgb(129, 180, 179)', 'rgb(124, 103, 37)']
irises_colors = ['rgb(33, 75, 99)', 'rgb(79, 129, 102)', 'rgb(151, 179, 100)',
                 'rgb(175, 49, 35)', 'rgb(36, 73, 147)']
cafe_colors =  ['rgb(146, 123, 21)', 'rgb(177, 180, 34)', 'rgb(206, 206, 40)',
                'rgb(175, 51, 21)', 'rgb(35, 36, 21)']

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
                dbc.CardHeader(html.Label(['Gráfico de Torta'],style={'font-weight': 'bold', "text-align": "left"})),
                dbc.CardBody([
                    dbc.Spinner(
                        dcc.Graph(id='cht-pie-chart'),
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
                    html.Label(['Datos:'],style={'font-weight': 'bold', "text-align": "left"}),
                    dcc.Dropdown(
                        id='dpd-column-lists',
                        clearable=False,
                        multi=True
                    ),
                    html.Br(),
                    dcc.RadioItems(
                        id="rdi_pie_type",
                        options=[
                            {'label': '  Torta', 'value': 'PIE'},
                            {'label': '  Dona', 'value': 'DNA'},
                        ],
                        value='PIE'
                    ),
                    html.Br(),
                    html.Label(['Color:'],style={'font-weight': 'bold', "text-align": "left"}),
                    dcc.Dropdown(
                        id='dpd-color-lists',
                        clearable=False,
                        options=[
                            {'label': 'Night Colors', 'value': 'night_colors'},
                            {'label': 'Sunflowers Colors', 'value': 'sunflowers_colors'},
                            {'label': 'Irises Colors', 'value': 'irises_colors'},
                            {'label': 'Cafe colors', 'value': 'cafe_colors'},
                        ],
                        value='night_colors',
                    ),
                ])
            ]),
        ], width=3),
    ]),
])

@app.callback(
    Output('cht-pie-chart','figure'),
    [Input("btn_show_chart", "n_clicks"),
     Input('dpd-query-list', 'value'), 
     Input('dpd-well-list', 'value'),
     Input('dpd-column-lists', 'value'),
     Input('dtp_fecha', 'date'),
     Input('inp_chart_name', 'value'),
     Input('rdi_pie_type', 'value'),
     Input('dpd-color-lists', 'value')])
def update_bar_chart(n_clicks, file_name, well_name, columns_list, dtp_fecha, chart_title, pie_type, color_list):

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

                if pie_type=='PIE':
                    hueco= 0
                else:
                    hueco=.3

                for columna in columns_list:
                    fig = go.Figure(data=[go.Pie(labels=data_results['NOMBRE'],
                         values=data_results[columna],
                         hole=hueco)])
                if color_list=='night_colors':
                    fig.update_traces( marker_colors=night_colors)
                if color_list=='sunflowers_colors':
                    fig.update_traces( marker_colors=sunflowers_colors)
                if color_list=='irises_colors ':
                    fig.update_traces( marker_colors=irises_colors )
                if color_list=='cafe_colors ':
                    fig.update_traces( marker_colors=cafe_colors )
                fig.update_layout(
                    title={
                        'text': chart_title,
                        'y':0.9,
                        'x':0.1,
                        'xanchor': 'center',
                        'yanchor': 'top'})
                fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
                fig.update_layout(legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ))
    return fig

@app.callback(
    [Output('dpd-column-lists','options'),
    Output('dpd-column-lists','value')],
    [Input('dpd-query-list', 'value')])
def update_column_list(file_name):

    data_results = pd.DataFrame()
    columns = [{'label': i, 'value': i} for i in []]
    quer= ''
    valor=[]
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
                valor.append(data_results.columns[0])
    return columns, valor