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
from datetime import date
from collections import OrderedDict
import base64
import json
import os
import dash_daq as daq

from app import app
from library import create_chart, update_columns_list, search_unit, find_file

#Definir imagenes
open_chart = '.\pictures\open_chart.png'
open_chart_base64 = base64.b64encode(open(open_chart, 'rb').read()).decode('ascii')

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

query = "SELECT NOMBRE FROM VARIABLES"
var_list =pd.read_sql(query, con)
var_list = var_list.sort_values('NOMBRE')['NOMBRE'].unique()

#Listado de eventos
query = "SELECT * FROM EVENTOS"
event_list =pd.read_sql(query, con)

#Listado de unidades por variables
query = "SELECT * FROM UNIDADES"
unidades =pd.read_sql(query, con)

#Listado de unidades por variables
query = "SELECT NOMBRE, FECHA, PRESION FROM PRESION_ROCIO"
press_rocio =pd.read_sql(query, con)

con.close()

#Listado de query
pathway = './querys'
files = [f for f in listdir(pathway) if isfile(join(pathway, f))]

file_name = ''
tab_height = '2vh'

layout = html.Div([
    dbc.Navbar(
        [
            dbc.Col([
            #********************** Cabecera ******************
            #
                dbc.Row([
                    dbc.Col([
                        html.Label(['Consulta:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                            id='dpd-consulta-lista',
                            options=[
                                {'label': i, 'value': i} for i in files
                            ],
                            clearable=False
                        ),
                    ], width={"size": 4, "offset": 1}),
                    dbc.Col([
                        html.Label(['Pozo:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                            id='dpd-pozo-lista',
                            options=[{'label': i, 'value': i} for i in well_list],
                            clearable=True,
                            multi=False,
                        ),
                    ], width={"size": 4, "offset": 0}),
                ]),
            ], width={"size": 6, "offset": 0}),
            dbc.Col([
                dbc.Row([
                    dbc.Col([
                        html.Label(['Nombre Plantilla:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dbc.Input(id="inp-ruta-linechart", placeholder="Type something...", type="text", style={'backgroundColor':'white'}),
                    ], width={"size": 3, "offset": 1}),
                     dbc.Col([
                        html.Label(['Grafico Simple:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Upload(
                            dbc.Button(
                                html.Span(["Abrir ", html.I(className="fas fa-upload ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                                n_clicks=0, color="primary", className="mr-3"
                            ),
                            id='btn_open_linechart',
                            multiple=False
                        ),
                    ], width={"size": 2, "offset": 0}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button(html.Span(["Guardar ", html.I(className="fas fa-save ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                            id="btn_save_linechart", 
                            n_clicks=0, 
                            color="primary", 
                            className="mr-3"
                        ),
                        html.Div(id="save_message_linechart"),
                    ], width={"size": 2, "offset": 0}),
                    dbc.Col([
                        html.Label(['Grafico Triple:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Upload(
                            dbc.Button(
                                html.Span(["Abrir ", html.I(className="fas fa-upload ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                                n_clicks=0, color="primary", className="mr-3"
                            ),
                            id='btn_open_triplechart',
                            multiple=False
                        ),
                    ], width={"size": 2, "offset": 0}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button(html.Span(["Guardar ", html.I(className="fas fa-save ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                            id="btn_save_Triplechart", 
                            n_clicks=0, 
                            color="primary", 
                            className="mr-3"
                        ),
                        html.Div(id="save_message_Triplechart"),
                    ], width={"size": 1, "offset": 0}),
                ]),
                html.Br(),
            ], width={"size": 6, "offset": 0}),
        ],
        color="#F9FCFC",
        dark=True,
    ),
    html.Br(),
    dcc.Tabs(style={
        'width': '50%',
        'font-size': '100%',
        'height':tab_height
    },children=[
        #*********************************** Primer Tab *********************************
        #
        dcc.Tab(label='Grafico Simple', style={'font-weight': 'bold','padding': '0','line-height': tab_height},selected_style={'padding': '0','line-height': tab_height}, children=[
            dbc.Row([
                dbc.Col([
                    html.Br(),
                    dbc.Button(
                        html.Span(["Mostrar ", html.I(className="fas fa-chart-bar ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                        id="btn_show_chart",
                        color="success",
                        className="me-1"
                    )
                ]),
            ]),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dac.Box([
                        dac.BoxHeader(
                            collapsible = False,
                            closable = False,
                            title="Gráfico de Líneas"
                        ),
                        dac.BoxBody(
                            dcc.Loading(
                                dcc.Graph(id='cht-line-chart', style={"width": "100%" }),
                            ),
                        ),	
                        ],
                        color='primary',
                        solid_header=True,
                        elevation=4,
                        width=12,
                    ),
                ], width={"size": 9,"offset": 0}),
                dbc.Col([
                    dac.Box([
                        dac.BoxHeader(
                            collapsible = False,
                            closable = False,
                            title="Parametros"
                        ),
                        dac.BoxBody([
                            dcc.Tabs(style={
                                'width': '50%',
                                'font-size': '100%',
                                'height':tab_height
                            },children=[
                                dcc.Tab(label='Opciones', style={'padding': '0','line-height': tab_height},selected_style={'padding': '0','line-height': tab_height}, children=[
                                    html.Br(),
                                    dcc.Checklist(
                                        id="cb_clear_data_line",
                                        options=[{"label": "  Limpiar valores Ceros", "value": "YES"}],
                                        value=[],
                                        labelStyle={"display": "inline-block"},
                                    ),
                                    dcc.Checklist(
                                        id="cb_group_by",
                                        options=[{"label": "  Aplicar agrupacion por fecha:", "value": "YES"}],
                                        value=[],
                                        labelStyle={"display": "inline-block"},
                                    ),
                                    dcc.RadioItems(
                                        id='rb-func-aggregation',
                                        options=[
                                            {'label': ' Sumatoria  ', 'value': 'SUM'},
                                            {'label': ' Media', 'value': 'MEAN'},
                                        ],
                                        value='SUM',
                                        labelStyle={'display': 'inline-block', 'padding':'10px'},
                                    ),
                                    html.Br(),
                                    dbc.Card([
                                        dbc.CardHeader(html.Label(['Eje Y Primario'],style={'font-weight': 'bold', "text-align": "left"})),
                                        dbc.CardBody([
                                            dbc.Row([
                                                dbc.Col([
                                                    html.Label(['Datos:'],style={'font-weight': 'bold', "text-align": "left"}),
                                                    dcc.Dropdown(
                                                        id='dpd-column-list-y1',
                                                        clearable=False,
                                                        multi=True
                                                    ),
                                                ]),
                                            ]),
                                            dbc.Row([
                                                dbc.Col([
                                                    html.Label(['color:'],style={'font-weight': 'bold', "text-align": "left"}),
                                                    dbc.Input(
                                                        type="color",
                                                        id="inp-color-list-y1",
                                                        value="#1530E3",
                                                        style={"width": 75, "height": 50},
                                                    ),
                                                ]),
                                                dbc.Col([
                                                    html.Label(['Estilo:'],style={'font-weight': 'bold', "text-align": "left"}),
                                                    dcc.Dropdown(
                                                        id='dpd-LineStile-y1',
                                                        options=[
                                                            {'label': 'Solid', 'value': 'solid'},
                                                            {'label': 'Dash', 'value': 'dash'},
                                                            {'label': 'Dot', 'value': 'dot'},
                                                            {'label': 'Dash-dot', 'value': 'dashdot'},
                                                        ],
                                                        value='solid',
                                                        clearable=False,
                                                        multi=False,
                                                    ),
                                                ]),
                                            ]),
                                        ]),
                                    ]),
                                    dbc.Card([
                                        dbc.CardHeader(html.Label(['Eje Y Secundario'],style={'font-weight': 'bold', "text-align": "left"})),
                                        dbc.CardBody([
                                            dbc.Row([
                                                dbc.Col([
                                                    html.Label(['Datos:'],style={'font-weight': 'bold', "text-align": "left"}),
                                                    dcc.Dropdown(
                                                        id='dpd-column-list-y2',
                                                        clearable=False,
                                                        multi=True
                                                    ),
                                                ]),
                                            ]),
                                            dbc.Row([
                                                dbc.Col([
                                                    html.Label(['color:'],style={'font-weight': 'bold', "text-align": "left"}),
                                                    dbc.Input(
                                                        type="color",
                                                        id="inp-color-list-y2",
                                                        value="#1530E3",
                                                        style={"width": 75, "height": 50},
                                                    ),
                                                ]),
                                                dbc.Col([
                                                    html.Label(['Estilo:'],style={'font-weight': 'bold', "text-align": "left"}),
                                                    dcc.Dropdown(
                                                        id='dpd-LineStile-y2',
                                                        options=[
                                                            {'label': 'Solid', 'value': 'solid'},
                                                            {'label': 'Dash', 'value': 'dash'},
                                                            {'label': 'Dot', 'value': 'dot'},
                                                            {'label': 'Dash-Dot', 'value': 'dashdot'},
                                                        ],
                                                        value='solid',
                                                        clearable=False,
                                                        multi=False,
                                                    ),
                                                ]),
                                            ]),
                                        ]),
                                    ]),
                                    dbc.Card([
                                        dbc.CardBody([
                                            html.Label(['Variable Calculadas:'],style={'font-weight': 'bold', "text-align": "left"}),
                                            dcc.Dropdown(
                                                id='dpd-var-list-chart',
                                                options=[{'label': i, 'value': i} for i in var_list],
                                                clearable=False,
                                                multi=True,
                                            ),
                                        ])
                                    ]),
                                ]),
                                dcc.Tab(label='Eventos', style={'padding': '0','line-height': tab_height},selected_style={'padding': '0','line-height': tab_height},children=[
                                    dbc.Card([
                                        dbc.CardHeader(html.Label(['Eventos'],style={'font-weight': 'bold', "text-align": "left"})),
                                        dbc.CardBody([
                                            dbc.Col([
                                                    html.Label(['color fondo:'],style={'font-weight': 'bold', "text-align": "left"}),
                                                    dbc.Input(
                                                        type="color",
                                                        id="inp-color-annotation",
                                                        value="#ecebda",
                                                        style={"width": 75, "height": 50},
                                                    ),
                                                ]),
                                            daq.ToggleSwitch(
                                                id='ts-annotation',
                                                value=True,
                                                label='Mostrar Eventos',
                                                labelPosition='top'
                                            ),
                                            dash_table.DataTable(id="dt_table_event", 
                                                columns = [{'name': i, 'id': i} for i in event_list.columns],
                                                data = event_list.to_dict('records'),
                                                style_as_list_view=True,
                                                style_cell={'padding': '5px', 'textAlign':'left','fontSize':12, 'font-family':'arial'},
                                                style_table={
                                                    'overflowX': 'auto',
                                                    'whiteSpace': 'normal',
                                                    'height': 'auto',
                                                },
                                                page_size= 5,
                                                style_header={
                                                    'backgroundColor': 'blue',
                                                    'fontWeight': 'bold',
                                                    'color': 'white',
                                                    'textAlign':'center',
                                                    'fontSize':10,
                                                    'font-family':'arial'
                                                },),
                                            daq.ToggleSwitch(
                                                id='ts-rocio',
                                                value=False,
                                                label='Mostrar Presión de Rocio',
                                                labelPosition='top'
                                            ),
                                            dash_table.DataTable(id="dt_table_rocio", 
                                                columns = [{'name': i, 'id': i} for i in press_rocio.columns],
                                                data = press_rocio.to_dict('records'),
                                                style_as_list_view=True,
                                                style_cell={'padding': '5px', 'textAlign':'left','fontSize':12, 'font-family':'arial'},
                                                style_table={
                                                    'overflowX': 'auto',
                                                    'whiteSpace': 'normal',
                                                    'height': 'auto',
                                                },
                                                page_size= 5,
                                                style_header={
                                                    'backgroundColor': 'blue',
                                                    'fontWeight': 'bold',
                                                    'color': 'white',
                                                    'textAlign':'center',
                                                    'fontSize':10,
                                                    'font-family':'arial'
                                                },),
                                        ]),
                                    ], style={"background-color": "#F9FCFC"},),
                                ]),
                            ]),
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
        ]),
        #*********************************** Sedundo Tab *************************************
        #
        dcc.Tab(label='Gráfico Triple', style={'font-weight': 'bold','padding': '0','line-height': tab_height},selected_style={'padding': '0','line-height': tab_height}, children=[
            dbc.Row([
                dbc.Col([
                    html.Br(),
                    dbc.Button(
                        html.Span(["Mostrar ", html.I(className="fas fa-chart-bar ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                        id="btn_show_chart_triple",
                        color="success",
                        className="me-1"
                    )
                ]),
            ]),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dac.Box([
                        dac.BoxHeader(
                            collapsible = False,
                            closable = False,
                            title="Gráfico Nro 1 "
                        ),
                        dac.BoxBody(
                            dcc.Loading(
                                dcc.Graph(id='cht-line-chart1', style={"width": "100%" }),
                            ),
                        ),	
                        ],
                        color='primary',
                        solid_header=True,
                        elevation=4,
                        width=12
                    ),
                ], width={"size": 9,"offset": 0}),
                dbc.Col([
                    dac.Box([
                        dac.BoxHeader(
                            collapsible = False,
                            closable = False,
                            title="Parametros "
                        ),
                        dac.BoxBody([
                            dbc.Row([
                                dbc.Col([
                                    dcc.Checklist(
                                        id="cb_clear_data_line1",
                                        options=[{"label": "  Limpiar valores Ceros", "value": "YES"}],
                                        value=[],
                                        labelStyle={"display": "inline-block"},
                                    ),
                                    html.Br(),
                                    html.Label(['Eje Primario:'],style={'font-weight': 'bold', "text-align": "left"}),
                                    dcc.Dropdown(
                                        id='dpd-column-chart1-y1',
                                        clearable=False,
                                        multi=True
                                    ),
                                ]),
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    html.Label(['color:'],style={'font-weight': 'bold', "text-align": "left"}),
                                    dbc.Input(
                                        type="color",
                                        id="inp-color-chart1-y1",
                                        value="#1530E3",
                                        style={"width": 75, "height": 50},
                                    ),
                                ]),
                                dbc.Col([
                                    html.Label(['Estilo:'],style={'font-weight': 'bold', "text-align": "left"}),
                                    dcc.Dropdown(
                                        id='dpd-LineStile-chart1-y1',
                                        options=[
                                            {'label': 'Solid', 'value': 'solid'},
                                            {'label': 'Dash', 'value': 'dash'},
                                            {'label': 'Dot', 'value': 'dot'},
                                            {'label': 'Dash-dot', 'value': 'dashdot'},
                                        ],
                                        value='solid',
                                        clearable=False,
                                        multi=False,
                                    ),
                                ]),
                            ]),
                            html.Br(),
                            dbc.Row([
                                dbc.Col([
                                    html.Label(['Eje Secundario:'],style={'font-weight': 'bold', "text-align": "left"}),
                                    dcc.Dropdown(
                                        id='dpd-column-chart1-y2',
                                        clearable=False,
                                        multi=True
                                    ),
                                ]),
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    html.Label(['color:'],style={'font-weight': 'bold', "text-align": "left"}),
                                    dbc.Input(
                                        type="color",
                                        id="inp-color-chart1-y2",
                                        value="#1530E3",
                                        style={"width": 75, "height": 50},
                                    ),
                                ]),
                                dbc.Col([
                                    html.Label(['Estilo:'],style={'font-weight': 'bold', "text-align": "left"}),
                                    dcc.Dropdown(
                                        id='dpd-LineStile-chart1-y2',
                                        options=[
                                            {'label': 'Solid', 'value': 'solid'},
                                            {'label': 'Dash', 'value': 'dash'},
                                            {'label': 'Dot', 'value': 'dot'},
                                            {'label': 'Dash-dot', 'value': 'dashdot'},
                                        ],
                                        value='solid',
                                        clearable=False,
                                        multi=False,
                                    ),
                                ]),
                            ]),
                            html.Br(),
                            html.Label(['Variable Calculadas:'],style={'font-weight': 'bold', "text-align": "left"}),
                            dcc.Dropdown(
                                id='dpd-var-chart1',
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
                ], width={"size": 3,"offset": 0}),
            ]),
            dbc.Row([
                dbc.Col([
                    dac.Box([
                        dac.BoxHeader(
                            collapsible = False,
                            closable = False,
                            title="Gráfico Nro 2 "
                        ),
                        dac.BoxBody(
                            dcc.Loading(
                                dcc.Graph(id='cht-line-chart2', style={"width": "100%" }),
                            ),
                        ),	
                        ],
                        color='primary',
                        solid_header=True,
                        elevation=4,
                        width=12
                    ),
                ], width={"size": 9,"offset": 0}),
                dbc.Col([
                    dac.Box([
                        dac.BoxHeader(
                            collapsible = False,
                            closable = False,
                            title="Parametros"
                        ),
                        dac.BoxBody([
                            dbc.Row([
                                dbc.Col([
                                    dcc.Checklist(
                                        id="cb_clear_data_line2",
                                        options=[{"label": "  Limpiar valores Ceros", "value": "YES"}],
                                        value=[],
                                        labelStyle={"display": "inline-block"},
                                    ),
                                    html.Br(),
                                    html.Label(['Eje Primario:'],style={'font-weight': 'bold', "text-align": "left"}),
                                    dcc.Dropdown(
                                        id='dpd-column-chart2-y1',
                                        clearable=False,
                                        multi=True
                                    ),
                                ]),
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    html.Label(['color:'],style={'font-weight': 'bold', "text-align": "left"}),
                                    dbc.Input(
                                        type="color",
                                        id="inp-color-chart2-y1",
                                        value="#1530E3",
                                        style={"width": 75, "height": 50},
                                    ),
                                ]),
                                dbc.Col([
                                    html.Label(['Estilo:'],style={'font-weight': 'bold', "text-align": "left"}),
                                    dcc.Dropdown(
                                        id='dpd-LineStile-chart2-y1',
                                        options=[
                                            {'label': 'Solid', 'value': 'solid'},
                                            {'label': 'Dash', 'value': 'dash'},
                                            {'label': 'Dot', 'value': 'dot'},
                                            {'label': 'Dash-dot', 'value': 'dashdot'},
                                        ],
                                        value='solid',
                                        clearable=False,
                                        multi=False,
                                    ),
                                ]),
                            ]),
                            html.Br(),
                            dbc.Row([
                                dbc.Col([
                                    html.Label(['Eje Secundario:'],style={'font-weight': 'bold', "text-align": "left"}),
                                    dcc.Dropdown(
                                        id='dpd-column-chart2-y2',
                                        clearable=False,
                                        multi=True
                                    ),
                                ]),
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    html.Label(['color:'],style={'font-weight': 'bold', "text-align": "left"}),
                                    dbc.Input(
                                        type="color",
                                        id="inp-color-chart2-y2",
                                        value="#1530E3",
                                        style={"width": 75, "height": 50},
                                    ),
                                ]),
                                dbc.Col([
                                    html.Label(['Estilo:'],style={'font-weight': 'bold', "text-align": "left"}),
                                    dcc.Dropdown(
                                        id='dpd-LineStile-chart2-y2',
                                        options=[
                                            {'label': 'Solid', 'value': 'solid'},
                                            {'label': 'Dash', 'value': 'dash'},
                                            {'label': 'Dot', 'value': 'dot'},
                                            {'label': 'Dash-dot', 'value': 'dashdot'},
                                        ],
                                        value='solid',
                                        clearable=False,
                                        multi=False,
                                    ),
                                ]),
                            ]),
                            html.Br(),
                            html.Label(['Variable Calculadas:'],style={'font-weight': 'bold', "text-align": "left"}),
                            dcc.Dropdown(
                                id='dpd-var-chart2',
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
                ], width={"size": 3,"offset": 0}),
            ]),
            dbc.Row([
                dbc.Col([
                    dac.Box([
                        dac.BoxHeader(
                            collapsible = False,
                            closable = False,
                            title="Gráfico Nro 3 "
                        ),
                        dac.BoxBody(
                            dcc.Loading(
                                dcc.Graph(id='cht-line-chart3', style={"width": "100%" }),
                            ),
                        ),	
                        ],
                        color='primary',
                        solid_header=True,
                        elevation=4,
                        width=12
                    ),
                ], width={"size": 9,"offset": 0}),
                dbc.Col([
                    dac.Box([
                        dac.BoxHeader(
                            collapsible = False,
                            closable = False,
                            title="Parametros"
                        ),
                        dac.BoxBody([
                            dbc.Row([
                                dbc.Col([
                                    dcc.Checklist(
                                        id="cb_clear_data_line3",
                                        options=[{"label": "  Limpiar valores Ceros", "value": "YES"}],
                                        value=[],
                                        labelStyle={"display": "inline-block"},
                                    ),
                                    html.Br(),
                                    html.Label(['Eje Primario:'],style={'font-weight': 'bold', "text-align": "left"}),
                                    dcc.Dropdown(
                                        id='dpd-column-chart3-y1',
                                        clearable=False,
                                        multi=True
                                    ),
                                ]),
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    html.Label(['color:'],style={'font-weight': 'bold', "text-align": "left"}),
                                    dbc.Input(
                                        type="color",
                                        id="inp-color-chart3-y1",
                                        value="#1530E3",
                                        style={"width": 75, "height": 50},
                                    ),
                                ]),
                                dbc.Col([
                                    html.Label(['Estilo:'],style={'font-weight': 'bold', "text-align": "left"}),
                                    dcc.Dropdown(
                                        id='dpd-LineStile-chart3-y1',
                                        options=[
                                            {'label': 'Solid', 'value': 'solid'},
                                            {'label': 'Dash', 'value': 'dash'},
                                            {'label': 'Dot', 'value': 'dot'},
                                            {'label': 'Dash-dot', 'value': 'dashdot'},
                                        ],
                                        value='solid',
                                        clearable=False,
                                        multi=False,
                                    ),
                                ]),
                            ]),
                            html.Br(),
                            dbc.Row([
                                dbc.Col([
                                    html.Label(['Eje Secundario:'],style={'font-weight': 'bold', "text-align": "left"}),
                                    dcc.Dropdown(
                                        id='dpd-column-chart3-y2',
                                        clearable=False,
                                        multi=True
                                    ),
                                ]),
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    html.Label(['color:'],style={'font-weight': 'bold', "text-align": "left"}),
                                    dbc.Input(
                                        type="color",
                                        id="inp-color-chart3-y2",
                                        value="#1530E3",
                                        style={"width": 75, "height": 50},
                                    ),
                                ]),
                                dbc.Col([
                                    html.Label(['Estilo:'],style={'font-weight': 'bold', "text-align": "left"}),
                                    dcc.Dropdown(
                                        id='dpd-LineStile-chart3-y2',
                                        options=[
                                            {'label': 'Solid', 'value': 'solid'},
                                            {'label': 'Dash', 'value': 'dash'},
                                            {'label': 'Dot', 'value': 'dot'},
                                            {'label': 'Dash-dot', 'value': 'dashdot'},
                                        ],
                                        value='solid',
                                        clearable=False,
                                        multi=False,
                                    ),
                                ]),
                            ]),
                            html.Br(),
                            html.Label(['Variable Calculadas:'],style={'font-weight': 'bold', "text-align": "left"}),
                            dcc.Dropdown(
                                id='dpd-var-chart3',
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
                ], width={"size": 3,"offset": 0}),
            ]),
        ]),
    ]),
    dbc.Modal(
        [
            dbc.ModalHeader("Plantilla Salvada"),
        ],
        id="modal_line",
        is_open=False,
    ),
    dbc.Modal(
        [
            dbc.ModalHeader("Plantilla Salvada"),
        ],
        id="modal_error_line",
        is_open=False,
    ),
])

@app.callback(
    [Output('cht-line-chart','figure'),
    Output("modal_error_line", "children"),
     Output("modal_error_line", "is_open")],
    [Input("btn_show_chart", "n_clicks"),
     Input('dpd-consulta-lista', 'value'), 
     Input('dpd-pozo-lista', 'value'),
     Input('dpd-column-list-y1', 'value'),
     Input('dpd-column-list-y2', 'value'),
     Input('ts-annotation', 'value'), 
     Input('dt_table_event', 'data'),
     Input('dpd-var-list-chart', 'value'),
     Input('inp-color-list-y1', 'value'),
     Input('inp-color-list-y2', 'value'),
     Input('cb_clear_data_line', 'value'),
     Input('dpd-LineStile-y1', 'value'),
     Input('dpd-LineStile-y2', 'value'),
     Input('inp-color-annotation', 'value'),
     Input('cb_group_by', 'value'),
     Input('rb-func-aggregation','value'),
     Input('ts-rocio','value'),
     Input('dt_table_rocio','data')],
     [State("modal_error_line", "is_open"),
    State("modal_error_line", "children")]
    )
def update_line_chart(n_clicks, file_name, well_name, column_list_y1, column_list_y2, show_annot, annot_data, var_list, color_y1, color_y2, clear_data, stile_y1, stile_y2, anno_color, group_by, aggregation_func, show_rocio, rocio_data, is_open, children):

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    if 'btn_show_chart' in changed_id:
        if column_list_y1 or column_list_y2:
            try:
                fig = create_chart(archivo, unidades, file_name, well_name, column_list_y1, column_list_y2, show_annot, annot_data, var_list, color_y1, color_y2, clear_data, stile_y1, stile_y2, anno_color, group_by, aggregation_func, show_rocio, rocio_data)
            except Exception  as e:
                    is_open = True
                    children = [dbc.ModalHeader("Error"),
                        dbc.ModalBody(
                            html.H6('Probelmas con la consulta, error: {}'.format(e), style={'textAlign': 'center', 'padding': 10}),
                        ),
                    ]
    return fig, children, is_open

@app.callback(
    [Output('cht-line-chart1','figure'),
     Output('cht-line-chart2','figure'),
     Output('cht-line-chart3','figure'),],
    [Input("btn_show_chart_triple", "n_clicks"),
     Input('dpd-consulta-lista', 'value'), 
     Input('dpd-pozo-lista', 'value'),
	 Input('dpd-column-chart1-y1', 'value'),
     Input('dpd-column-chart1-y2', 'value'),
     Input('dpd-column-chart2-y1', 'value'),
     Input('dpd-column-chart2-y2', 'value'),
     Input('dpd-column-chart3-y1', 'value'),
     Input('dpd-column-chart3-y2', 'value'),
     Input('dpd-var-chart1', 'data'),
     Input('dpd-var-chart2', 'data'),
     Input('dpd-var-chart3', 'data'),
	 Input('inp-color-chart1-y1','value'),
	 Input('inp-color-chart1-y2','value'),
     Input('inp-color-chart2-y1','value'),
	 Input('inp-color-chart2-y2','value'),
     Input('inp-color-chart3-y1','value'),
	 Input('inp-color-chart3-y2','value'),
     Input('cb_clear_data_line1', 'value'),
     Input('cb_clear_data_line2', 'value'),
     Input('cb_clear_data_line3', 'value'), 
     Input('dpd-LineStile-chart1-y1', 'value'),
     Input('dpd-LineStile-chart1-y2', 'value'),
     Input('dpd-LineStile-chart2-y1', 'value'),
     Input('dpd-LineStile-chart2-y2', 'value'),
     Input('dpd-LineStile-chart3-y1', 'value'),
     Input('dpd-LineStile-chart3-y2', 'value'),
     ])
def update_triple_chart(n_clicks, file_name, well_name, cols_chart1_y1, cols_chart1_y2, cols_chart2_y1, 
   cols_chart2_y2, cols_chart3_y1, cols_chart3_y2, var_list1,  var_list2, var_list3, color_chart1_y1,color_chart1_y2, 
   color_chart2_y1,color_chart2_y2, color_chart3_y1,color_chart3_y2, clear_data_chart1, clear_data_chart2, clear_data_chart3, 
   stile_chart1_y1, stile_chart1_y2, stile_chart2_y1, stile_chart2_y2, stile_chart3_y1, stile_chart3_y2):

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    fig1 = {}
    fig2 = {}
    fig3 = {}
    
    if 'btn_show_chart' in changed_id:
        fig1 = create_chart(archivo,  unidades, file_name, well_name, cols_chart1_y1, cols_chart1_y2, False, [], var_list1, color_chart1_y1, color_chart1_y2, clear_data_chart1, stile_chart1_y1, stile_chart1_y2, '#ecebda', [], [], False, None)
        fig2 = create_chart(archivo,  unidades, file_name, well_name, cols_chart2_y1, cols_chart2_y2, False, [], var_list2, color_chart2_y1, color_chart2_y2, clear_data_chart2, stile_chart2_y1, stile_chart2_y2, '#ecebda', [], [], False, None)
        fig3 = create_chart(archivo,  unidades, file_name, well_name, cols_chart3_y1, cols_chart3_y2, False, [], var_list3, color_chart3_y1, color_chart3_y2, clear_data_chart3, stile_chart3_y1, stile_chart3_y2, '#ecebda', [], [], False, None)

    return fig1, fig2, fig3

@app.callback(
    [Output('dpd-column-list-y1','options'),
     Output('dpd-column-list-y2','options')],
     Output('dpd-column-chart1-y1', 'options'),
     Output('dpd-column-chart1-y2', 'options'),
     Output('dpd-column-chart2-y1', 'options'),
     Output('dpd-column-chart2-y2', 'options'),
     Output('dpd-column-chart3-y1', 'options'),
     Output('dpd-column-chart3-y2', 'options'),
    [Input('dpd-consulta-lista', 'value'),
     Input('dpd-var-list-chart', 'value')])
def update_column_list(file_name, var_list):

    columns = [{'label': i, 'value': i} for i in []]
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'dpd-consulta-lista' in changed_id or 'dpd-var-list-chart' in changed_id:
        columns = update_columns_list(archivo, file_name, var_list)

    return columns, columns, columns, columns, columns, columns, columns, columns

@app.callback(
    Output('modal_line','is_open'),
    [Input('btn_save_linechart', 'n_clicks'),
    Input('btn_save_Triplechart','n_clicks'),
    Input('dpd-consulta-lista', 'value'),
    Input('dpd-column-list-y1', 'value'),
    Input('dpd-column-list-y2', 'value'),
    Input('inp-ruta-linechart', 'value'),
    Input('dpd-var-list-chart', 'value'),
    Input('inp-color-list-y1', 'value'), 
    Input('inp-color-list-y2', 'value'),
    Input('ts-annotation', 'value'), 
    Input('dpd-LineStile-y2', 'value'),
    Input('dpd-LineStile-y2', 'value'),
    Input("cb_clear_data_line1", "value"),
    Input("dpd-column-chart1-y1", "value"),
    Input("inp-color-chart1-y1", "value"),
    Input("dpd-LineStile-chart1-y1", "value"),
    Input("dpd-column-chart1-y2", "value"),
    Input("inp-color-chart1-y2", "value"),
    Input("dpd-LineStile-chart1-y2", "value"),
    Input("dpd-var-chart1", "value"),
    Input("cb_clear_data_line2", "value"),
    Input("dpd-column-chart2-y1", "value"),
    Input("inp-color-chart2-y1", "value"),
    Input("dpd-LineStile-chart2-y1", "value"),
    Input("dpd-column-chart2-y2", "value"),
    Input("inp-color-chart2-y2", "value"),
    Input("dpd-LineStile-chart2-y2", "value"),
    Input("dpd-var-chart2", "value"),
    Input("cb_clear_data_line3", "value"),
    Input("dpd-column-chart3-y1", "value"),
    Input("inp-color-chart3-y1", "value"),
    Input("dpd-LineStile-chart3-y1", "value"),
    Input("dpd-column-chart3-y2", "value"),
    Input("inp-color-chart3-y2", "value"),
    Input("dpd-LineStile-chart3-y2", "value"),
    Input("dpd-var-chart3", "value"),
    Input('cb_group_by', 'value'),
    State('modal_line', 'is_open')
    ]) 
def save_linechart(n_clicks, n_clicks2, consulta, datos_y1, datos_y2, file_name, var_list, color_y1,
    color_y2, text_annot, stile_y1, stile_y2, clear1, datos1_y1, color1_y1, stile1_y1,
    datos1_y2, color1_y2, stile1_y2, var_list1, clear2, datos2_y1, color2_y1, stile2_y1,
    datos2_y2, color2_y2, stile2_y2, var_list2, clear3, datos3_y1, color3_y1, stile3_y1,
    datos3_y2, color3_y2, stile3_y2, var_list3, group_by, is_open ):
    mensaje=''
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'btn_save_linechart' in changed_id:
        if file_name:
            data = {}
            data['grafico'] = []
            data['grafico'].append({
                'consulta': consulta,
                'datos_y1': datos_y1,
                'datos_y2': datos_y2,
                'var_list': var_list,
                'color_y1': color_y1,
                'color_y2': color_y2,
                'annotation': text_annot,
                'stile_y1' : stile_y1,
                'stile_y2' : stile_y2,
                'group_by': group_by,
                })
            with open(CHART_DIRECTORY+file_name, 'w') as file:
                json.dump(data, file, indent=4)
            is_open = True

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'btn_save_Triplechart' in changed_id:
        if file_name:
            data = {}
            data['grafico'] = []
            data['grafico'].append({
                'consulta': consulta,
                'clear1': clear1,
                'datos1_y1': datos1_y1,
                'color1_y1': color1_y1,
                'stile1_y1': stile1_y1,
                'datos1_y2': datos1_y2,
                'color1_y2': color1_y2,
                'stile1_y2': stile1_y2,
                'var_list1': var_list1,
                'clear2': clear2,
                'datos2_y1': datos2_y1,
                'color2_y1': color2_y1,
                'stile2_y1': stile2_y1,
                'datos2_y2': datos2_y2,
                'color2_y2': color2_y2,
                'stile2_y2': stile2_y2,
                'var_list2': var_list2,
                'clear3': clear3,
                'datos3_y1': datos3_y1,
                'color3_y1': color3_y1,
                'stile3_y1': stile3_y1,
                'datos3_y2': datos3_y2,
                'color3_y2': color3_y2,
                'stile3_y2': stile3_y2,
                'var_list3': var_list3,
                })
            with open(CHART_DIRECTORY+file_name, 'w') as file:
                json.dump(data, file, indent=4)
            is_open = True

    return is_open

@app.callback( [Output('inp-ruta-linechart', 'value'),
                Output('dpd-consulta-lista', 'value'),
                Output('dpd-column-list-y1', 'value'),
                Output('dpd-column-list-y2', 'value'),
                Output('dpd-var-list-chart', 'value'),
                Output('inp-color-list-y1', 'value'),
                Output('inp-color-list-y2', 'value'),
                Output('ts-annotation', 'value'),
                Output('dpd-LineStile-y1', 'value'),
                Output('dpd-LineStile-y2', 'value'),

                Output("dpd-column-chart1-y1", "value"),
                Output("inp-color-chart1-y1", "value"),
                Output("dpd-LineStile-chart1-y1", "value"),
                Output("dpd-column-chart1-y2", "value"),
                Output("inp-color-chart1-y2", "value"),
                Output("dpd-LineStile-chart1-y2", "value"),
                Output("dpd-var-chart1", "value"),
                Output("cb_clear_data_line1", "value"),

                Output("dpd-column-chart2-y1", "value"),
                Output("inp-color-chart2-y1", "value"),
                Output("dpd-LineStile-chart2-y1", "value"),
                Output("dpd-column-chart2-y2", "value"),
                Output("inp-color-chart2-y2", "value"),
                Output("dpd-LineStile-chart2-y2", "value"),
                Output("dpd-var-chart2", "value"),
                Output("cb_clear_data_line2", "value"),

                Output("dpd-column-chart3-y1", "value"),
                Output("inp-color-chart3-y1", "value"),
                Output("dpd-LineStile-chart3-y1", "value"),
                Output("dpd-column-chart3-y2", "value"),
                Output("inp-color-chart3-y2", "value"),
                Output("dpd-LineStile-chart3-y2", "value"),
                Output("dpd-var-chart3", "value"),
                Output("cb_clear_data_line3", "value"),
                Output('cb_group_by', 'value'),

                ],
              [Input('btn_open_linechart', 'filename'),
              Input('btn_open_linechart', 'contents'),
              Input('btn_open_triplechart','filename'),
              Input('btn_open_triplechart','contents')]
              )
def open_linechart( list_of_names, list_of_contents, triple_file_name, triple_file_contents):
    archivo = list_of_names
    consulta=[]
    datos_y1=[]
    datos_y2=[]
    var_list=[]
    datos1_y1=[]
    datos1_y2=[]
    var_list1=[]
    datos2_y1=[]
    datos2_y2=[]
    var_list2=[]
    datos3_y1=[]
    datos3_y2=[]
    var_list3=[]
    clear1=[]
    clear2=[]
    clear3=[]
    color_y1="#1530E3"
    color_y2="#1530E3"
    color1_y1="#1530E3"
    color1_y2="#1530E3"
    color2_y1="#1530E3"
    color2_y2="#1530E3"
    color3_y1="#1530E3"
    color3_y2="#1530E3"
    text_annot=False
    stile_y1='solid'
    stile_y2='solid'
    stile1_y1='solid'
    stile1_y2='solid'
    stile2_y1='solid'
    stile2_y2='solid'
    stile3_y1='solid'
    stile3_y2='solid'
    group_by=[]

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'btn_open_linechart' in changed_id:

        if list_of_names is not None:
            archivo = list_of_names
            with open(CHART_DIRECTORY+archivo) as file:
                data = json.load(file)
                for drop_values   in data['grafico']:
                    consulta = str(drop_values['consulta'])
                    datos_y1 = drop_values['datos_y1']
                    datos_y2 = drop_values['datos_y2']
                    var_list = drop_values['var_list']
                    color_y1 = drop_values['color_y1']
                    color_y2 = drop_values['color_y2']
                    text_annot = drop_values['annotation']
                    stile_y1 = drop_values['stile_y1']
                    stile_y2 = drop_values['stile_y2']
                    group_by = drop_values['group_by']

    if 'btn_open_triplechart.contents' in changed_id:

        if triple_file_name is not None:
            archivo = triple_file_name
            with open(CHART_DIRECTORY+archivo) as file:
                data = json.load(file)
                for drop_values   in data['grafico']:
                    consulta = str(drop_values['consulta'])
                    datos1_y1 = drop_values['datos1_y1']
                    datos1_y2 = drop_values['datos1_y2']
                    var_list1 = drop_values['var_list1']
                    color1_y1 = drop_values['color1_y1']
                    color1_y2 = drop_values['color1_y2']
                    stile1_y1= drop_values['stile1_y1']
                    stile1_y2= drop_values['stile1_y2']
                    clear1 = drop_values['clear1']

                    datos2_y1 = drop_values['datos2_y1']
                    datos2_y2 = drop_values['datos2_y2']
                    var_list2 = drop_values['var_list2']
                    color2_y1 = drop_values['color2_y1']
                    color2_y2 = drop_values['color2_y2']
                    stile2_y1= drop_values['stile2_y1']
                    stile2_y2= drop_values['stile2_y2']
                    clear2 = drop_values['clear2']

                    datos3_y1 = drop_values['datos3_y1']
                    datos3_y2 = drop_values['datos3_y2']
                    var_list3 = drop_values['var_list3']
                    color3_y1 = drop_values['color3_y1']
                    color3_y2 = drop_values['color3_y2']
                    stile3_y1= drop_values['stile3_y1']
                    stile3_y2= drop_values['stile3_y2']
                    clear3 = drop_values['clear3']


    return archivo, consulta, datos_y1, datos_y2, var_list, color_y1, color_y2, text_annot, stile_y1, stile_y2, datos1_y1, color1_y1, stile1_y1, datos1_y2, color1_y2, stile1_y2, var_list1, clear1, datos2_y1, color2_y1, stile2_y1, datos2_y2, color2_y2, stile2_y2, var_list2, clear2, datos3_y1, color3_y1, stile3_y1, datos3_y2, color3_y2, stile3_y2, var_list3, clear3,group_by

