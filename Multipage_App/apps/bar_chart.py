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
from library import search_unit, search_list, search_calcv

#Variable con la ruta para salvar los querys
QUERY_DIRECTORY = "./querys"
CHART_DIRECTORY = "./template/"

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

query = "SELECT NOMBRE FROM VARIABLES"
var_list =pd.read_sql(query, con)
var_list = var_list.sort_values('NOMBRE')['NOMBRE'].unique()

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
                    ], width={"size": 2, "offset": 1}),
                    dbc.Col([
                        html.Label(['Pozo:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                            id='dpd-well-list',
                            options=[{'label': i, 'value': i} for i in well_list],
                            clearable=False,
                            multi=True
                        ),
                    ], width={"size": 3, "offset": 0}),
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
                    ], width={"size": 3, "offset": 0}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button(html.Span(["Mostrar ", html.I(className="fas fa-chart-bar ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                         id="btn_show_barchart", color="success", className="mr-3"),
                    ], width={"size": 1, "offset": 0}),
                ]),
                html.Br(),
            ], style={"background-color": "#F9FCFC"},),
        ], width={"size": 12, "offset": 0}),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.Row([
                    dbc.Col([
                        html.Label(['Nombre Plantilla:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dbc.Input(id="inp-ruta-barchart", placeholder="Type something...", type="text", style={'backgroundColor':'white'}),
                    ], width={"size": 3, "offset": 1}),
                     dbc.Col([
                        html.Br(),
                        dcc.Upload(
                            dbc.Button(html.Span(["Abrir ", html.I(className="fas fa-upload ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                             n_clicks=0, color="primary", className="mr-3"),
                            id='btn_open_barchart',
                            multiple=False
                        ),
                    ], width={"size": 3, "offset": 0}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button(html.Span(["Grabar ", html.I(className="fas fa-save ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                         id="btn_save_barchart", n_clicks=0, color="primary", className="mr-3"),
                        html.Div(id="save_message_barchart"),
                    ]),
                ]),
                html.Br(),
            ], style={"background-color": "#F9FCFC"},),
        ], width={"size": 6, "offset": 0}),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dac.Box([
                dac.BoxHeader(
                    collapsible = False,
                    closable = False,
                    title="Gráfico de Barra"
                ),
                dac.BoxBody(
                    dbc.Spinner(
                        dcc.Graph(id='cht-bar-chart', style={"width": "100%"}),
                    ),
                ),	
                ],
                color='primary',
                solid_header=True,
                elevation=4,
                width=12
            ),
        ], width=9),
        dbc.Col([
            dac.Box([
                dac.BoxHeader(
                    collapsible = False,
                    closable = False,
                    title="Opciones"
                ),
                dac.BoxBody([
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
                    html.Label(['Variable Calculadas:'],style={'font-weight': 'bold', "text-align": "left"}),
                    dcc.Dropdown(
                        id='dpd-var-list-barchart',
                        options=[{'label': i, 'value': i} for i in var_list],
                        clearable=False,
                        multi=True,
                    ),
                ]),	
                ],
                color='primary',
                solid_header=True,
                elevation=4,
                width=12,
                style={"background-color": "#F9FCFC"},
            ),
        ], width=3),
    ]),
    dbc.Modal(
        [
            dbc.ModalHeader("Plantilla Salvada"),
        ],
        id="modal_bar",
        is_open=False,
    ),
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
     Input('rdi_staked_columns', 'value'),
     Input('dpd-var-list-barchart', 'value')])
def update_bar_chart(n_clicks, file_name, well_name, columns_list, dtp_start_date, dtp_end_date, chart_title, staked_columns, var_list):

    df = pd.DataFrame()
    query= ''
    fecha_inicio = str(dtp_start_date)
    fecha_fin = str(dtp_end_date)
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    fig = {}
    if 'btn_show_barchart' in changed_id:
        con = sqlite3.connect(archivo)
        query= ''
        if file_name:
            with open(os.path.join(QUERY_DIRECTORY, file_name)) as f:
                contenido = f.readlines()
            if contenido:
                if fecha_inicio:
                    for linea in contenido:
                        query +=  linea
                    if query.find("WHERE")>0:
                        query += " AND date(FECHA)>='"+fecha_inicio+"' AND  date(FECHA)<='"+fecha_fin+"' ORDER BY FECHA"
                    else:
                        query += " WHERE date(FECHA)>='"+fecha_inicio+"' AND  date(FECHA)<='"+fecha_fin+"' ORDER BY FECHA"
                else:
                    for linea in contenido:
                        query +=  linea 
                df =pd.read_sql(query, con)

                if var_list:
                    for columna in df.columns:
                        if columna != 'FECHA' and columna != 'NOMBRE':
                            df[columna] = pd.to_numeric(df[columna])

                    for var in var_list:
                        requisitos_list, titulo, ecuacion = search_calcv( archivo, var)

                        if search_list(requisitos_list, df.columns.tolist()):
                            df[titulo] =eval(ecuacion)
                            var_name = titulo

                if well_name is not None and columns_list:
                    df= df[df['NOMBRE'].isin(well_name)]
                    #Se asegura que el dataframe tenga datos
                    if len(df)>0:
                        if staked_columns=='STC':
                            fig = px.bar(df, x="NOMBRE", y=columns_list,  height=700,  
                            title=chart_title, animation_group="NOMBRE", barmode='stack', animation_frame="FECHA" )
                        else:
                            fig = px.bar(df, x="NOMBRE", y=columns_list,  height=700,  
                            title=chart_title,  animation_group="NOMBRE", barmode='group', animation_frame="FECHA")
    return fig

@app.callback(
    Output('dpd-column-list','options'),
    [Input('dpd-query-list-bar', 'value'),
    Input('dpd-var-list-barchart', 'value')])
def update_column_list(file_name, var_list):

    df = pd.DataFrame()
    con = sqlite3.connect(archivo)
    columns = [{'label': i, 'value': i} for i in []]
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'dpd-query-list-bar' in changed_id or 'dpd-var-list-barchart' in changed_id:
        query= ''
        if file_name:
            with open(os.path.join(QUERY_DIRECTORY, file_name)) as f:
                contenido = f.readlines()
                for linea in contenido:
                    query +=  linea

                #Filtrar solo la primera fila
                query += " LIMIT 1"

                df =pd.read_sql(query, con)

            if var_list is not None:
                for columna in df.columns:
                    if columna != 'FECHA' and columna != 'NOMBRE':
                        df[columna] = pd.to_numeric(df[columna])

                for var in var_list:
                    requisitos_list, titulo, ecuacion = search_calcv( archivo, var)

                    if search_list(requisitos_list, df.columns.tolist()):
                        df[titulo] =eval(ecuacion)
                        var_name = titulo

            if  df.columns[2]=='FECHA':
                columns=[{'label': i, 'value': i} for i in df.columns[3:]]
            else:
                columns=[{'label': i, 'value': i} for i in df.columns[2:]]

    con.close()

    return columns

@app.callback(
    Output('modal_bar','is_open'),
    [Input('btn_save_barchart', 'n_clicks'),
    Input('dpd-query-list-bar', 'value'),
    Input('dpd-column-list', 'value'),
    Input('inp-ruta-barchart', 'value'),
    Input('dpd-var-list-barchart', 'value'),
    Input('inp_barchart_name', 'value'),
    State("modal_bar", "is_open")
    ]) 
def save_bar_chart(n_clicks, consulta, datos_y1, file_name, var_list, chart_title, is_open ):
    mensaje=''
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'btn_save_barchart' in changed_id:
        data = {}
        data['grafico'] = []
        data['grafico'].append({
            'consulta': consulta,
            'datos_y1': datos_y1,
            'var_list': var_list,
            'chart_title': chart_title,})
        if file_name:
            with open(CHART_DIRECTORY+file_name, 'w') as file:
                json.dump(data, file, indent=4)
            is_open = True
    return is_open

@app.callback( [Output('inp-ruta-barchart', 'value'),
                Output('dpd-query-list-bar', 'value'),
                Output('dpd-column-list', 'value'),
                Output('dpd-var-list-barchart', 'value'),
                Output('inp_barchart_name', 'value')],
              [Input('btn_open_barchart', 'filename'),
              Input('btn_open_barchart', 'contents')]
              )
def open_bar_chart( list_of_names, list_of_contents):
    archivo = list_of_names
    consulta=[]
    datos_y1=[]
    var_list=[]
    chart_title=[]

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'btn_open_barchart' in changed_id:
        if list_of_names is not None:
            print(list_of_names)
            archivo = list_of_names
            with open(CHART_DIRECTORY+archivo) as file:
                data = json.load(file)
                for drop_values   in data['grafico']:
                    consulta = str(drop_values['consulta'])
                    datos_y1 = drop_values['datos_y1']
                    var_list = drop_values['var_list']
                    chart_title = drop_values['chart_title']
    return archivo, consulta, datos_y1, var_list, chart_title   