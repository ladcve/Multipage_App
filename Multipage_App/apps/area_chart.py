import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Row import Row
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
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
                            clearable=False
                        ),
                    ], width={"size": 2, "offset": 1}),
                    dbc.Col([
                        html.Label(['Pozo:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                            id='dpd-well-list-area',
                            options=[{'label': i, 'value': i} for i in well_list],
                            clearable=False,
                            multi=False
                        ),
                    ], width={"size": 3, "offset": 0}),
                    dbc.Col([
                        html.Label(['Fecha: '],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.DatePickerRange(
                            id='dtp_fecha_area',
                            min_date_allowed= date(1995, 8, 5),
                            max_date_allowed=date.today(),
                            start_date = date.today()- timedelta(days=-7),
                            end_date=date.today(),
                            display_format='YYYY-MM-DD',
                            style={'backgroundColor':'white'},
                        )
                    ], width={"size": 2, "offset": 0}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button(html.Span(["Mostrar ", html.I(className="fas fa-chart-bar ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                         id="btn_show_areachart", color="success", className="mr-3"),
                    ], width={"size": 1, "offset": 0}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button(html.Span(["Exportar Imagen ", html.I(className="fas fa-file-export ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                         id="btn_export_areaimg", color="warning", className="mr-3"),
                    ], width={"size": 1, "offset": 0}),
                ]),
                html.Br(),
            ]),
        ], width={"size": 11, "offset": 0}),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.Row([
                    dbc.Col([
                        html.Label(['Nombre Archivo:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dbc.Input(id="inp-ruta-areachart", placeholder="Type something...", type="text", style={'backgroundColor':'white'}),
                    ], width={"size": 3, "offset": 1}),
                     dbc.Col([
                        html.Br(),
                        dcc.Upload(
                            dbc.Button(html.Span(["Abrir Grafico ", html.I(className="fas fa-upload ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                             n_clicks=0, color="primary", className="mr-3"),
                            id='btn_open_areachart',
                            multiple=False
                        ),
                    ], width={"size": 3, "offset": 0}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button(html.Span(["Grabar Grafico ", html.I(className="fas fa-save ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                         id="btn_save_barchart", n_clicks=0, color="primary", className="mr-3"),
                        html.Div(id="save_message_areachart"),
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
                dbc.CardHeader(html.Label(['Gráfico de Área'],style={'font-weight': 'bold', "text-align": "left"})),
                dbc.CardBody([
                    dbc.Spinner(
                        dcc.Graph(id='cht-area-chart',style={"height": 600, "width":1000}),
                    ),
                ])
            ]),
        ], width=9),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.Label(['Opciones'],style={'font-weight': 'bold', "text-align": "left"})),
                dbc.CardBody([
                    html.Label(['Nombre del Gráfico'],style={'font-weight': 'bold', "text-align": "left"}),
                    dbc.Input(id="inp_areachart_name", placeholder="Type something...", type="text", style={'backgroundColor':'white'}),
                    html.Br(),
                    html.Label(['Datos eje Y:'],style={'font-weight': 'bold', "text-align": "left"}),
                    dcc.Dropdown(
                        id='dpd-column-list-ejey',
                        clearable=False,
                        multi=True
                    ),
                ])
            ]),
            dbc.Card([
                dbc.CardBody([
                    html.Label(['Variable Calculadas:'],style={'font-weight': 'bold', "text-align": "left"}),
                    dcc.Dropdown(
                        id='dpd-var-list-areachart',
                        options=[{'label': i, 'value': i} for i in var_list],
                        clearable=False,
                        multi=True,
                    ),
                ])
            ]),
        ], width=3),
    ]),
])

@app.callback(
    Output('cht-area-chart','figure'),
    [Input("btn_show_areachart", "n_clicks"),
     Input('dpd-query-list-area', 'value'), 
     Input('dpd-well-list-area', 'value'),
     Input('dpd-column-list-ejey', 'value'),
     Input('dtp_fecha_area', 'start_date'),
     Input('dtp_fecha_area', 'end_date'),
     Input('inp_areachart_name', 'date'),
     Input('dpd-var-list-areachart', 'value')])
def update_bar_chart(n_clicks, file_name, well_name, columns_list, dtp_start_date, dtp_end_date, chart_title, var_list):

    df = pd.DataFrame()
    query= ''
    fecha_inicio = str(dtp_start_date)
    fecha_fin = str(dtp_end_date)
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    fig = {}
    if 'btn_show_chart' in changed_id:
        con = sqlite3.connect(archivo)
        query = "SELECT * FROM VARIABLES"
        variables =pd.read_sql(query, con)
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
                    df= df[df['NOMBRE']==well_name]
                fig = px.area(df, x="FECHA", y=columns_list, title=chart_title)
    return fig

@app.callback(
    Output('dpd-column-list-ejey','options'),
    [Input('dpd-query-list-area', 'value'),
    Input('dpd-var-list-areachart', 'value')])
def update_column_list(file_name, var_list):

    df = pd.DataFrame()
    columns = [{'label': i, 'value': i} for i in []]
    quer= ''
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'dpd-query-list' in changed_id:
        con = sqlite3.connect(archivo)
        query = "SELECT * FROM VARIABLES"
        variables =pd.read_sql(query, con)

        if file_name is not None:
            with open(os.path.join(QUERY_DIRECTORY, file_name)) as f:
                contenido = f.readlines()
                for linea in contenido:
                    query =  linea
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
    Input('pd-column-list-ejey', 'value'),
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
                Output('pd-column-list-ejey', 'value'),
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