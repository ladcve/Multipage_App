import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Row import Row
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from plotly.subplots import make_subplots
from dash_table.Format import Format, Symbol
import dash_admin_components as dac
import plotly.graph_objects as go
import plotly.express as px
import plotly.express as px
import dash_table
import sqlite3
import configparser
import sys
import json
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
from library import reform_df, search_unit, search_calcv, search_list

#Variable con la ruta para salvar los querys
QUERY_DIRECTORY = "./querys"
TEMPLATE_DIRECTORY = "./template/"

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

#Listado de variables calculadas
query = "SELECT NOMBRE FROM VARIABLES"
var_list =pd.read_sql(query, con)
var_list = var_list.sort_values('NOMBRE')['NOMBRE'].unique()

#Listado de unidades por variables
query = "SELECT * FROM UNIDADES"
unidades =pd.read_sql(query, con)

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
                            id='dpd-query-list-area',
                            options=[
                                {'label': i, 'value': i} for i in files
                            ],
                            clearable=False,
                            multi=False
                        ),
                    ], width={"size": 3, "offset": 1}),
                    dbc.Col([
                        html.Label(['Pozo:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                            id='dpd-well-list-area',
                            options=[{'label': i, 'value': i} for i in well_list],
                            clearable=False,
                            multi=False,
                        ),
                    ], width={"size": 3, "offset": 0}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button(html.Span(["Mostrar ", html.I(className="fas fa-chart-bar ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                         id="btn_show_areachart", color="success", className="mr-3"),
                    ], width={"size": 1, "offset": 0}),
                ]),
                html.Br(),
            ], style={"background-color": "#F9FCFC"},),
        ], width={"size": 8, "offset": 0}),
        dbc.Col([
            dbc.Card([
                dbc.Row([
                    dbc.Col([
                        html.Label(['Nombre Plantilla:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dbc.Input(id="inp-ruta-areachart", placeholder="Type something...", type="text", style={'backgroundColor':'white'}),
                    ], width={"size": 4, "offset": 1}),
                     dbc.Col([
                        html.Br(),
                        dcc.Upload(
                            dbc.Button(html.Span(["Abrir ", html.I(className="fas fa-upload ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                             n_clicks=0, color="primary", className="mr-3"),
                            id='btn_open_areachart',
                            multiple=False
                        ),
                    ], width={"size": 2, "offset": 0}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button(html.Span(["Grabar ", html.I(className="fas fa-save ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                         id="btn_save_areachart", n_clicks=0, color="primary", className="mr-3"),
                        html.Div(id="save_message_areachart"),
                    ], width={"size": 1, "offset": 1}),
                ]),
                html.Br(),
            ], style={"background-color": "#F9FCFC"},),
        ], width={"size": 4, "offset": 0}),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dac.Box([
                    dac.BoxHeader(
                        collapsible = False,
                        closable = False,
                        title="Marcadores Estratgráficos"
                    ),
                    dac.BoxBody(
                        dcc.Loading(
                            dcc.Graph(id='cht-area-chart', style={"width": "100%"}),
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
                        title="Marcadores Estratgráficos"
                    ),
                    dac.BoxBody([
                        html.Label(['Nombre del Gráfico'],style={'font-weight': 'bold', "text-align": "left"}),
                        dbc.Input(id="inp_areachart_name", placeholder="Type something...", type="text", style={'backgroundColor':'white'}),
                        html.Br(),
                        html.Label(['Datos eje Y1:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                            id='dpd-column-list-ejey1-area',
                            clearable=False,
                            multi=True
                        ),
                        html.Label(['color:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dbc.Input(
                            type="color",
                            id="inp-color-y1",
                            value="#1530E3",
                            style={"width": 75, "height": 50},
                        ),
                        html.Br(),
                        html.Label(['Datos eje Y2:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                            id='dpd-column-list-ejey2-area',
                            clearable=False,
                            multi=True
                        ),
                        html.Label(['color:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dbc.Input(
                            type="color",
                            id="inp-color-y2",
                            value="#1530E3",
                            style={"width": 75, "height": 50},
                        ),
                        html.Br(),
                        html.Label(['Modo:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                            id='dpd-mode',
                            options=[
                                {'label': 'Línea', 'value': 'lines'},
                                {'label': 'Nada', 'value': 'none'},
                            ],
                            value='lines'
                        ),
                        html.Br(),
                        html.Label(['Variable Calculadas:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                            id='dpd-var-list-areachart',
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
        id="modal_area",
        is_open=False,
    ),
    dbc.Modal(
        [
            dbc.ModalHeader("Plantilla Salvada"),
        ],
        id="modal_error_area",
        is_open=False,
    ),
])
@app.callback(
    [Output('cht-area-chart','figure'),
    Output("modal_error_area", "children"),
     Output("modal_error_area", "is_open")],
    [Input("btn_show_areachart", "n_clicks"),
     Input('dpd-query-list-area', 'value'), 
     Input('dpd-well-list-area', 'value'),
     Input('dpd-column-list-ejey1-area', 'value'),
     Input('dpd-column-list-ejey2-area', 'value'),
     Input('inp_areachart_name', 'date'),
     Input('dpd-mode', 'value'),
     Input('inp-color-y1', 'value'),
     Input('inp-color-y2', 'value'),
     Input('dpd-var-list-areachart', 'value')],
     [State("modal_error_area", "is_open"),
    State("modal_error_area", "children")])
def update_bar_chart(n_clicks, file_name, well_name, columns_list_y1, columns_list_y2, chart_title, type_mode, color_y1, color_y2, var_list, is_open, children):

    color_axis_y1 = dict(hex=color_y1)
    color_axis_y2 = dict(hex=color_y2)
    df = pd.DataFrame()
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    if 'btn_show_areachart' in changed_id:
        con = sqlite3.connect(archivo)
        query = "SELECT * FROM VARIABLES"
        variables =pd.read_sql(query, con)
        query=''
        if file_name is not None:
            try:
                with open(os.path.join(QUERY_DIRECTORY, file_name)) as f:
                    contenido = f.readlines()
                if contenido is not None:
                    for linea in contenido:
                        query +=  linea 

                    

                    df =pd.read_sql(query, con)
                    df =df.sort_values("FECHA")

                    if var_list is not None:
                        for columna in df.columns:
                            if columna != 'FECHA' and columna != 'NOMBRE':
                                df[columna] = pd.to_numeric(df[columna])

                        for var in var_list:
                            requisitos_list, titulo, ecuacion = search_calcv( archivo, var)

                            if search_list(requisitos_list, df.columns.tolist()):
                                df[titulo] =eval(ecuacion)
                                var_name = titulo
                    
                    if well_name is not None:
                        df= df[df['NOMBRE']==well_name]

                    i=1

                    for columnas_y1 in columns_list_y1:
                        var_name, var_color = search_unit(unidades, columnas_y1)

                        if color_axis_y1 == {'hex': '#1530E3'} and var_color:
                            color_axis_y1 = dict(hex=var_color)

                        fig.add_trace(
                            go.Scatter(x=df['FECHA'],
                                y=df[columnas_y1],
                                name=var_name,
                                mode=type_mode,
                                line_color=color_axis_y1["hex"],
                                yaxis= 'y'+ str(i),
                                fill='tozeroy'
                            ),
                            secondary_y=False,
                        )
                        i=+1
                    for columnas_y2 in columns_list_y2:
                        var_name, var_color = search_unit(unidades, columnas_y2)

                        if color_axis_y2 == {'hex': '#1530E3'} and var_color:
                            color_axis_y2 = dict(hex=var_color)

                        fig.add_trace(
                            go.Scatter(x=df['FECHA'],
                                y=df[columnas_y2],
                                name=var_name,
                                mode=type_mode,
                                fill='tonexty',
                                line_color=color_axis_y2["hex"],
                                yaxis= 'y'+ str(i),
                            ),
                            secondary_y=True,
                        )
                        i=+1

                    fig.update_layout(
                        autosize=False,
                        title=chart_title,
                        hovermode='x unified',
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgb(240, 240, 240)',
                        height=700,
                        margin=dict(
                            l=50,
                            r=50,
                            b=100,
                            t=100,
                            pad=4,
                        ),
                    )
                    fig.update_xaxes(
                        rangeslider_visible=True,
                            rangeselector=dict(
                                buttons=list([
                                dict(count=1, label="1m", step="month", stepmode="backward"),
                                dict(count=6, label="6m", step="month", stepmode="backward"),
                                dict(count=1, label="YTD", step="year", stepmode="todate"),
                                dict(count=1, label="1y", step="year", stepmode="backward"),
                                dict(step="all")
                                ])
                            )
                        )
                    fig.update_layout(legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    ))
            except Exception  as e:
                    is_open = True
                    children = [dbc.ModalHeader("Error"),
                        dbc.ModalBody(
                            html.H6('Error: {}'.format(e), style={'textAlign': 'center', 'padding': 10}),
                        ),
                    ]
    return fig, children, is_open

@app.callback(
    [Output('dpd-column-list-ejey1-area','options'),
    Output('dpd-column-list-ejey2-area','options')],
    [Input('dpd-query-list-area', 'value'),
    Input('dpd-var-list-areachart', 'value')])
def update_column_list(file_name, var_list):

    df = pd.DataFrame()
    columns = [{'label': i, 'value': i} for i in []]
    query= ''
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'dpd-query-list-area' in changed_id or 'dpd-var-list-areachart' in changed_id:
        con = sqlite3.connect(archivo)
        query= ''
        if file_name:
            with open(os.path.join(QUERY_DIRECTORY, file_name)) as f:
                contenido = f.readlines()
                for linea in contenido:
                    query +=  linea
                query += " LIMIT 1"
                df =pd.read_sql(query, con)

                if var_list is not None:
                    for columna in df.columns:
                        if columna != 'FECHA' and columna != 'NOMBRE':
                            df[columna] = pd.to_numeric(df[columna])

                    for var in var_list:
                        requisitos_list, titulo, ecuacion = search_calcv( archivo, var)

                        if search_list(requisitos_list, df.columns.tolist()):
                            evalu = eval(ecuacion)
                            df[titulo] = evalu


                if  df.columns[2]=='FECHA':
                    columns=[{'label': i, 'value': i} for i in df.columns[3:]]
                else:
                    columns=[{'label': i, 'value': i} for i in df.columns[2:]]
        con.close()
        
    return columns, columns

@app.callback(
    Output("modal_area", "is_open"),
    [Input('btn_save_areachart', 'n_clicks'),
    Input('dpd-query-list-area', 'value'),
    Input('dpd-column-list-ejey1-area', 'value'),
    Input('dpd-column-list-ejey2-area', 'value'),
    Input('inp-ruta-areachart', 'value'),
    Input('dpd-mode', 'value'),
    Input('inp-color-y1', 'value'),
    Input('inp-color-y2', 'value'),
    Input('dpd-var-list-areachart', 'value'),
    State("modal_area", "is_open")
    ]) 
def save_area_chart(n_clicks, consulta, datos_y1,datos_y2, file_name, type_mode, color_y1, color_y2, var_list, is_open ):
    mensaje=''
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'btn_save_areachart' in changed_id:
        data = {}
        data['grafico'] = []
        data['grafico'].append({
            'consulta': consulta,
            'datos_y1': datos_y1,
            'datos_y2': datos_y2,
            'var_list': var_list,
            'type_mode': type_mode,
            'color_y1': color_y1,
            'color_y2': color_y2})
        if file_name:
            with open(TEMPLATE_DIRECTORY+file_name, 'w') as file:
                json.dump(data, file, indent=4)
            is_open = True
    return is_open

@app.callback( [Output('inp-ruta-areachart', 'value'),
                Output('dpd-query-list-area', 'value'),
                Output('dpd-column-list-ejey1-area', 'value'),
                Output('dpd-column-list-ejey2-area', 'value'),
                Output('dpd-var-list-areachart', 'value'),
                Output('dpd-mode', 'value'),
                Output('inp-color-y1', 'value'),
                Output('inp-color-y2', 'value'),],
              [Input('btn_open_areachart', 'filename'),
              Input('btn_open_areachart', 'contents')]
              )
def open_area_chart( list_of_names, list_of_contents):
    archivo = list_of_names
    consulta=[]
    datos_y1=[]
    datos_y2=[]
    var_list=[]
    type_mode='lines'
    color_y1="#1530E3"
    color_y2="#1530E3"

    if list_of_names is not None:
        print(list_of_names)
        archivo = list_of_names
        with open(TEMPLATE_DIRECTORY+archivo) as file:
            data = json.load(file)
            for drop_values   in data['grafico']:
                consulta = str(drop_values['consulta'])
                datos_y1 = drop_values['datos_y1']
                datos_y2 = drop_values['datos_y2']
                type_mode = drop_values['type_mode']
                color_y1 = drop_values['color_y1']
                color_y2 = drop_values['color_y2']
    return archivo, consulta, datos_y1,datos_y2, var_list, type_mode, color_y1, color_y2