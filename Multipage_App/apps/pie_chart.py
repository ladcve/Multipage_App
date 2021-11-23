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
            dbc.Card([
                dbc.Row([
                    dbc.Col([
                        html.Label(['Consulta:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                            id='dpd-query-list-pie',
                            options=[
                                {'label': i, 'value': i} for i in files
                            ],
                            clearable=False
                        ),
                    ], width={"size": 3, "offset": 1}),
                    dbc.Col([
                        html.Label(['Pozo:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                            id='dpd-well-list-pie',
                            options=[{'label': i, 'value': i} for i in well_list],
                            clearable=False,
                            multi=True
                        ),
                    ], width={"size": 4, "offset": 1}),
                    dbc.Col([
                        html.Label(['Fecha: '],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.DatePickerSingle(
                            id='dtp_fecha',
                            date=date.today(),
                            display_format='YYYY-MM-DD',
                            style={'backgroundColor':'white'},
                        )
                    ], width={"size": 2, "offset": 1}),
                ]),
                html.Br(),
            ]),
        ], width={"size": 8, "offset": 0}),
        dbc.Col([
            dbc.Card([
                dbc.Row([
                    dbc.Col([
                        html.Br(),
                        dbc.Button("Mostrar Grafico", id="btn_show_piechart", color="success", className="mr-3"),
                    ], width={"size": 2, "offset": 1}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button("Exportar Imagen", id="btn_export_pieimg", color="warning", className="mr-3"),
                    ], width={"size": 2, "offset": 1}),
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
                        dbc.Input(id="inp-ruta-piechart", placeholder="Type something...", type="text", style={'backgroundColor':'white'}),
                    ], width={"size": 3, "offset": 1}),
                     dbc.Col([
                        html.Br(),
                        dcc.Upload(
                            dbc.Button("Cargar Template", n_clicks=0, color="warning", className="mr-3"),
                            id='btn_open_piechart',
                            multiple=False
                        ),
                    ], width={"size": 3, "offset": 0}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button("Grabar Template", id="btn_save_piechart", n_clicks=0, color="warning", className="mr-3"),
                        html.Div(id="save_message_piechart"),
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
                    dbc.Input(id="inp_piechart_name", placeholder="Type something...", type="text", style={'backgroundColor':'white'}),
                    html.Br(),
                    html.Label(['Datos:'],style={'font-weight': 'bold', "text-align": "left"}),
                    dcc.Dropdown(
                        id='dpd-column-lists-pie',
                        clearable=False,
                        multi=True
                    ),
                    html.Br(),
                    html.Label(['Color:'],style={'font-weight': 'bold', "text-align": "left"}),
                    dcc.Dropdown(
                        id='dpd-color-lists-pie',
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
    [Input("btn_show_piechart", "n_clicks"),
     Input('dpd-query-list-pie', 'value'), 
     Input('dpd-well-list-pie', 'value'),
     Input('dpd-column-lists-pie', 'value'),
     Input('dtp_fecha', 'date'),
     Input('inp_piechart_name', 'value'),
     Input('dpd-color-lists-pie', 'value')])
def update_pie_chart(n_clicks, file_name, well_name, columns_list, dtp_fecha, chart_title, color_list):

    data_results = pd.DataFrame()
    quer= ''
    fecha = str(dtp_fecha)
    df = pd.DataFrame()

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
                    filtro = ['NOMBRE']
                    filtro.append(columna)
                    df2 = data_results[filtro]
                    df2.rename(columns={columna: "VOLUMEN"}, inplace=True)
                    df2['FLUIDO']=columna
                    df = df.append(df2)

                fig =px.sunburst(
                        df,
                        path=['NOMBRE', 'FLUIDO'],
                        values='VOLUMEN',
                        title=chart_title,
                    )
                if color_list=='night_colors':
                    fig.update_traces( marker_colors=night_colors)
                if color_list=='sunflowers_colors':
                    fig.update_traces( marker_colors=sunflowers_colors)
                if color_list=='irises_colors ':
                    fig.update_traces( marker_colors=irises_colors )
                if color_list=='cafe_colors ':
                    fig.update_traces( marker_colors=cafe_colors )

                fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
    return fig

@app.callback(
    [Output('dpd-column-lists-pie','options')],
    [Input('dpd-query-list-pie', 'value')])
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
    return columns

@app.callback(
    Output('save_message_piechart','children'),
    [Input('btn_save_piechart', 'n_clicks'),
    Input('dpd-query-list-pie', 'value'),
    Input('dpd-column-lists-pie', 'value'),
    Input('inp-ruta-piechart', 'value')]) 
def save_piechart(n_clicks, consulta, datos_y1, file_name ):
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

@app.callback( [Output('inp-ruta-piechart', 'value'),
                Output('dpd-query-list-pie', 'value'),
                Output('dpd-column-lists-pie', 'value'),],
              [Input('btn_open_piechart', 'filename'),
              Input('btn_open_piechart', 'contents')]
              )
def open_piechart( list_of_names, list_of_contents):
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