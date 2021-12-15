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

#Listado de variables calculadas
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
                            multi=True
                        ),
                    ], width={"size": 3, "offset": 0}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button(html.Span(["Mostrar ", html.I(className="fas fa-chart-bar ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                         id="btn_show_areachart", color="success", className="mr-3"),
                    ], width={"size": 1, "offset": 0}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button(html.Span(["Imagen ", html.I(className="fas fa-file-export ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                         id="btn_export_areaimg", color="warning", className="mr-3"),
                    ], width={"size": 1, "offset": 1}),
                ]),
                html.Br(),
            ]),
        ], width={"size": 8, "offset": 0}),
        dbc.Col([
            dbc.Card([
                dbc.Row([
                    dbc.Col([
                        html.Label(['Nombre Archivo:'],style={'font-weight': 'bold', "text-align": "left"}),
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
                    ], width={"size": 1, "offset": 0}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button(html.Span(["Grabar ", html.I(className="fas fa-save ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                         id="btn_save_areachart", n_clicks=0, color="primary", className="mr-3"),
                        html.Div(id="save_message_areachart"),
                    ], width={"size": 1, "offset": 1}),
                ]),
                html.Br(),
            ]),
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
                        dbc.Spinner(
                            dcc.Graph(id='cht-area-chart',style={"height": 600, "width":1100}),
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
                        html.Label(['Datos eje Y:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                            id='dpd-column-list-ejey-area',
                            clearable=False,
                            multi=True
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
                width=12
            ),
        ], width=3),
    ]),
])

@app.callback(
    Output('cht-area-chart','figure'),
    [Input("btn_show_areachart", "n_clicks"),
     Input('dpd-query-list-area', 'value'), 
     Input('dpd-well-list-area', 'value'),
     Input('dpd-column-list-ejey-area', 'value'),
     Input('inp_areachart_name', 'date'),
     Input('dpd-var-list-areachart', 'value')])
def update_bar_chart(n_clicks, file_name, well_name, columns_list, chart_title, var_list):

    df = pd.DataFrame()
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    fig = {}
    if 'btn_show_areachart' in changed_id:
        con = sqlite3.connect(archivo)
        query = "SELECT * FROM VARIABLES"
        variables =pd.read_sql(query, con)
        query=''
        if file_name is not None:
            with open(os.path.join(QUERY_DIRECTORY, file_name)) as f:
                contenido = f.readlines()
            if contenido is not None:
                for linea in contenido:
                    query +=  linea 

                df =pd.read_sql(query, con)
                df =df.sort_values("FECHA")

                if var_list is not None:
                    for var in var_list:
                        selec_var=variables.loc[variables['NOMBRE']==var]
                        ecuacion = selec_var.iloc[0]['ECUACION']
                        titulo = selec_var.iloc[0]['TITULO']
                        evalu = eval(ecuacion)
                        df[titulo] = evalu
                
                if well_name is not None:
                    df= df[df['NOMBRE'].isin(well_name)]

                if columns_list:
                    fig = px.area(df, x="FECHA", y=columns_list, title=chart_title)
                    fig.update_layout(
                        autosize=False,
                        hovermode='x unified',
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgb(240, 240, 240)',
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
    return fig

@app.callback(
    Output('dpd-column-list-ejey-area','options'),
    [Input('dpd-query-list-area', 'value'),
    Input('dpd-var-list-areachart', 'value')])
def update_column_list(file_name, var_list):

    df = pd.DataFrame()
    columns = [{'label': i, 'value': i} for i in []]
    query= ''
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'dpd-query-list' in changed_id:
        con = sqlite3.connect(archivo)
        query = "SELECT * FROM VARIABLES"
        variables =pd.read_sql(query, con)
        query= ''
        if file_name:
            with open(os.path.join(QUERY_DIRECTORY, file_name)) as f:
                contenido = f.readlines()
                for linea in contenido:
                    query +=  linea
                df =pd.read_sql(query, con)
                df =df.drop(['index', 'NOMBRE', 'FECHA'], axis=1)

                if var_list is not None:
                    for var in var_list:
                        selec_var=variables.loc[variables['NOMBRE']==var]
                        ecuacion = selec_var.iloc[0]['ECUACION']
                        titulo = selec_var.iloc[0]['TITULO']
                        evalu = eval(ecuacion)
                        df[titulo] = evalu


                columns = [{'label': i, 'value': i} for i in df.columns]
        con.close()
        
    return columns

@app.callback(
    Output('save_message_areachart','children'),
    [Input('btn_save_areachart', 'n_clicks'),
    Input('dpd-query-list-area', 'value'),
    Input('dpd-column-list-ejey-area', 'value'),
    Input('inp-ruta-areachart', 'value'),
    Input('dpd-var-list-areachart', 'value')]) 
def save_area_chart(n_clicks, consulta, datos_y1, file_name, var_list ):
    mensaje=''
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'btn_save_linechart' in changed_id:
        data = {}
        data['grafico'] = []
        data['grafico'].append({
            'consulta': consulta,
            'datos_y1': datos_y1,
            'var_list': var_list,})
        if file_name:
            with open(CHART_DIRECTORY+file_name, 'w') as file:
                json.dump(data, file, indent=4)
            mensaje = 'Archivo guardado'
    return mensaje

@app.callback( [Output('inp-ruta-areachart', 'value'),
                Output('dpd-query-list-area', 'value'),
                Output('dpd-column-list-ejey-area', 'value'),
                Output('dpd-var-list-areachart', 'value')],
              [Input('btn_open_areachart', 'filename'),
              Input('btn_open_areachart', 'contents')]
              )
def open_area_chart( list_of_names, list_of_contents):
    archivo = list_of_names
    consulta=[]
    datos_y1=[]
    var_list=[]

    if list_of_names is not None:
        print(list_of_names)
        archivo = list_of_names
        with open(CHART_DIRECTORY+archivo) as file:
            data = json.load(file)
            for drop_values   in data['grafico']:
                consulta = str(drop_values['consulta'])
                datos_y1 = drop_values['datos_y1']
                var_list = drop_values['var_list']
    return archivo, consulta, datos_y1, var_list