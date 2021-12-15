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

#Listado de variables calculadas
query = "SELECT NOMBRE FROM VARIABLES"
var_list =pd.read_sql(query, con)
var_list = var_list.sort_values('NOMBRE')['NOMBRE'].unique()

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
                            id='dpd-query-list-scatter',
                            options=[
                                {'label': i, 'value': i} for i in files
                            ],
                            clearable=False
                        ),
                    ], width={"size": 4, "offset": 1}),
                    dbc.Col([
                        html.Label(['Pozo:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                            id='dpd-well-list-scatter',
                            options=[{'label': i, 'value': i} for i in well_list],
                            clearable=False,
                            multi=False
                        ),
                    ], width={"size": 4, "offset": 0}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button(html.Span(["Mostrar ", html.I(className="fas fa-chart-bar ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                         id="btn_show_scatterchart", color="success", className="mr-3"),
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
                        dbc.Input(id="inp-ruta-scatterchart", placeholder="Type something...", type="text", style={'backgroundColor':'white'}),
                    ], width={"size": 3, "offset": 1}),
                     dbc.Col([
                        html.Br(),
                        dcc.Upload(
                            dbc.Button(html.Span(["Abrir ", html.I(className="fas fa-upload ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                              n_clicks=0, color="primary", className="mr-3"),
                            id='btn_open_scatterchart',
                            multiple=False
                        ),
                    ], width={"size": 1, "offset": 0}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button(html.Span(["Grabar ", html.I(className="fas fa-save ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                         id="btn_save_scatterchart", n_clicks=0, color="primary", className="mr-3"),
                        html.Div(id="save_message_scatter"),
                    ], width={"size": 1, "offset": 1}),
                ]),
                html.Br(),
            ]),
        ], width={"size": 6, "offset": 0}),
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
                            dcc.Graph(id='cht-scatter-chart',style={"height": 700, "width":1100}),
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
                        html.Label(['Eje X'],style={'font-weight': 'bold', "text-align": "left"}),
                        html.Label(['Datos:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                            id='dpd-column-list-x-scatter',
                            clearable=False,
                            multi=False
                        ),
                        html.Label(['Eje Y'],style={'font-weight': 'bold', "text-align": "left"}),
                        html.Label(['Datos:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                            id='dpd-column-list-y-scatter',
                            clearable=False,
                            multi=False
                        ),
                        html.Label(['Variable Calculadas:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                            id='dpd-var-list-scatterchart',
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
    Output('cht-scatter-chart','figure'),
    [Input("btn_show_scatterchart", "n_clicks"),
     Input('dpd-query-list-scatter', 'value'), 
     Input('dpd-well-list-scatter', 'value'),
     Input('dpd-column-list-x-scatter', 'value'),
     Input('dpd-column-list-y-scatter', 'value'),
     Input('dpd-var-list-scatterchart', 'value')])
def update_scatter_chart(n_clicks, file_name, well_name, column_list_x, column_list_y, var_list):

    df = pd.DataFrame()
    query= ''
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    fig = {}
    
    if 'btn_show_scatterchart' in changed_id:
        con = sqlite3.connect(archivo)
        query = "SELECT * FROM VARIABLES"
        variables =pd.read_sql(query, con)
        query= ''
        if file_name is not None:
            with open(os.path.join(QUERY_DIRECTORY, file_name)) as f:
                contenido = f.readlines()
            if contenido is not None:
                if well_name is not None:
                    for linea in contenido:
                        query +=  linea 
                    df =pd.read_sql(query, con)
                    df =df.sort_values("FECHA")
                    df = df[df['NOMBRE']==well_name]
                    if var_list is not None:
                        for var in var_list:
                            selec_var=variables.loc[variables['NOMBRE']==var]
                            ecuacion = selec_var.iloc[0]['ECUACION']
                            titulo = selec_var.iloc[0]['TITULO']
                            evalu = eval(ecuacion)
                            df[titulo] = evalu

                    fig = px.scatter(x=df[column_list_x],
                            y=df[column_list_y],)
                    fig.update_xaxes(title_text=column_list_x,showline=True, linewidth=2, linecolor='black', showgrid=False,)
                    fig.update_yaxes(title_text=column_list_y,showline=True, linewidth=2, linecolor='black', showgrid=False,)
                    fig.update_layout(
                        autosize=False,
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
    [Output('dpd-column-list-x-scatter','options'),
     Output('dpd-column-list-y-scatter','options')],
    [Input('dpd-query-list-scatter', 'value'),
    Input('dpd-var-list-scatterchart', 'value')])
def update_column_list(file_name, var_list):

    df = pd.DataFrame()
    columns = [{'label': i, 'value': i} for i in []]

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'dpd-query-list-scatter' in changed_id:
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
                if var_list is not None:
                    for var in var_list:
                        selec_var=variables.loc[variables['NOMBRE']==var]
                        ecuacion = selec_var.iloc[0]['ECUACION']
                        titulo = selec_var.iloc[0]['TITULO']
                        evalu = eval(ecuacion)
                        df[titulo] = evalu
                columns = [{'label': i, 'value': i} for i in df.columns]

        con.close()

    return columns, columns

@app.callback(
    Output('save_message_scatter','children'),
    [Input('btn_save_scatterchart', 'n_clicks'),
    Input('dpd-query-list-scatter', 'value'),
    Input('dpd-column-list-x-scatter', 'value'),
    Input('dpd-column-list-y-scatter', 'value'),
    Input('inp-ruta-scatterchart', 'value'),
    Input('dpd-var-list-scatterchart', 'value')]) 
def save_scatterchart(n_clicks, consulta, datos_y1, datos_y2, file_name, var_list ):
    mensaje=''
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'btn_save_scatterchart' in changed_id:
        data = {}
        data['grafico'] = []
        data['grafico'].append({
            'consulta': consulta,
            'datos_y1': datos_y1,
            'datos_y2': datos_y2,
            'var_list': var_list,})
        with open(CHART_DIRECTORY+file_name, 'w') as file:
            json.dump(data, file, indent=4)
        mensaje = 'Archivo guardado'
    return mensaje

@app.callback( [Output('inp-ruta-scatterchart', 'value'),
                Output('dpd-query-list', 'value'),
                Output('dpd-column-list-x', 'value'),
                Output('dpd-column-list-y', 'value'),
                Output('dpd-var-list-scatterchart', 'value')],
              [Input('btn_open_linechart', 'filename'),
              Input('btn_open_linechart', 'contents')]
              )
def open_scatterchart( list_of_names, list_of_contents):
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
                var_list = drop_values['var_list']
    return archivo, consulta, datos_y1, datos_y2