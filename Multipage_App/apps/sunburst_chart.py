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
from library import search_unit, search_list, search_calcv

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
                            clearable=False,
                            multi=False
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
                    ], width={"size": 3, "offset": 0}),
                    dbc.Col([
                        html.Label(['Fecha: '],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.DatePickerSingle(
                            id='dtp_fecha',
                            date=date.today(),
                            display_format='YYYY-MM-DD',
                            style={'backgroundColor':'white'},
                        )
                    ], width={"size": 1, "offset": 0}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button(html.Span(["Mostrar ", html.I(className="fas fa-chart-bar ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                         id="btn_show_piechart", color="success", className="mr-3"),
                    ], width={"size": 1, "offset": 1}),
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
                        dbc.Input(id="inp-ruta-piechart", placeholder="Type something...", type="text", style={'backgroundColor':'white'}),
                    ], width={"size": 3, "offset": 1}),
                     dbc.Col([
                        html.Br(),
                        dcc.Upload(
                            dbc.Button(html.Span(["Abrir ", html.I(className="fas fa-upload ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                             n_clicks=0, color="primary", className="mr-3"),
                            id='btn_open_piechart',
                            multiple=False
                        ),
                    ], width={"size": 1, "offset": 0}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button(html.Span(["Grabar  ", html.I(className="fas fa-save ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                         id="btn_save_piechart", n_clicks=0, color="primary", className="mr-3"),
                        html.Div(id="save_message_piechart"),
                    ], width={"size": 1, "offset": 1}),
                ]),
                html.Br(),
            ], style={"background-color": "#F9FCFC"},),
        ], width={"size": 5, "offset": 0}),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dac.Box([
                    dac.BoxHeader(
                        collapsible = False,
                        closable = False,
                        title="Gráfico de Sunburst"
                    ),
                    dac.BoxBody(
                        dbc.Spinner(
                            dcc.Graph(id='cht-pie-chart', style={"width": "100%"}),
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
                        html.Br(),
                        html.Label(['Variable Calculadas:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                            id='dpd-var-list-piechart',
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
])

@app.callback(
    Output('cht-pie-chart','figure'),
    [Input("btn_show_piechart", "n_clicks"),
     Input('dpd-query-list-pie', 'value'), 
     Input('dpd-well-list-pie', 'value'),
     Input('dpd-column-lists-pie', 'value'),
     Input('dtp_fecha', 'date'),    
     Input('inp_piechart_name', 'value'),
     Input('dpd-color-lists-pie', 'value'),
     Input('dpd-var-list-piechart', 'value')])
def update_pie_chart(n_clicks, file_name, well_name, columns_list, dtp_fecha, chart_title, color_list, var_list):

    df = pd.DataFrame()
    fecha = str(dtp_fecha)

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    fig = go.Figure()
    if 'btn_show_piechart' in changed_id:
        con = sqlite3.connect(archivo)
        query=''
        if file_name is not None:
            with open(os.path.join(QUERY_DIRECTORY, file_name)) as f:
                contenido = f.readlines()
            if contenido is not None:
                if fecha is not None:
                    for linea in contenido:
                        query +=  linea 

                    if query.find("WHERE")>-1 or query.find("where")>-1:
                        query += " AND date(FECHA)='"+fecha+"'"
                    else:
                        query += " WHERE date(FECHA)='"+fecha+"'"
                else:
                    for linea in contenido:
                        query +=  linea
                df =pd.read_sql(query, con)
                df =df.sort_values("FECHA")
                if well_name is not None:
                    df= df[df['NOMBRE'].isin(well_name)]

            if columns_list:
                if var_list is not None:
                    for columna in df.columns:
                        if columna != 'FECHA' and columna != 'NOMBRE':
                            df[columna] = pd.to_numeric(df[columna])

                    for var in var_list:
                        requisitos_list, titulo, ecuacion = search_calcv( archivo, var)
                        if search_list(requisitos_list, df.columns.tolist()):
                            df[titulo] =eval(ecuacion)
                            var_name = titulo

                df3 = pd.DataFrame()
                for columna in columns_list:
                    filtro = ['NOMBRE']
                    filtro.append(columna)
                    df2 = df[filtro]
                    df2.rename(columns={columna: "VOLUMEN"}, inplace=True)
                    df2['FLUIDO']=columna
                    df3 = df3.append(df2)
                if len(df)>0:
                    fig =px.sunburst(
                            df3,
                            path=['NOMBRE', 'FLUIDO'],
                            height=700,
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
    Output('dpd-column-lists-pie','options'),
    Input('dpd-query-list-pie', 'value'),
    Input('dpd-var-list-piechart', 'value')
    )
def update_column_list_pie(file_name, var_list):

    df = pd.DataFrame()
    columns = [{'label': i, 'value': i} for i in []]
    query= ''
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'dpd-query-list-pie' in changed_id or 'dpd-var-list-piechart' in changed_id:
        con = sqlite3.connect(archivo)
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
                        evalu = eval(ecuacion)
                        df[titulo] = evalu

            if  df.columns[2]=='FECHA':
                columns=[{'label': i, 'value': i} for i in df.columns[3:]]
            else:
                columns=[{'label': i, 'value': i} for i in df.columns[2:]]

        con.close()

    return columns

@app.callback(
    Output('save_message_piechart','children'),
    [Input('btn_save_piechart', 'n_clicks'),
    Input('dpd-query-list-pie', 'value'),
    Input('dpd-column-lists-pie', 'value'),
    Input('inp-ruta-piechart', 'value'),
    Input('dpd-var-list-piechart', 'value'),
    Input('dpd-color-lists-pie', 'value'),
    Input('inp_piechart_name', 'value'),
    ]) 
def save_piechart(n_clicks, consulta, datos_y1, file_name, var_list, color, chart_title ):
    mensaje=''
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'btn_save_linechart' in changed_id:
        data = {}
        data['grafico'] = []
        data['grafico'].append({
            'consulta': consulta,
            'datos_y1': datos_y1,
            'var_list': var_list,
            'color': color,
            'chart_title': chart_title,
            })
        if file_name:
            with open(CHART_DIRECTORY+file_name, 'w') as file:
                json.dump(data, file, indent=4)
            mensaje = 'Archivo guardado'
    return mensaje

@app.callback( [Output('inp-ruta-piechart', 'value'),
                Output('dpd-query-list-pie', 'value'),
                Output('dpd-column-lists-pie', 'value'),
                Output('dpd-var-list-piechart', 'value'),
                Output('dpd-color-lists-pie','value'),
                Output('inp_piechart_name', 'value')
                ],
              [Input('btn_open_piechart', 'filename'),
              Input('btn_open_piechart', 'contents'),]
              )
def open_piechart( list_of_names, list_of_contents):
    archivo = list_of_names
    consulta=[]
    datos_y1=[]
    var_list=[]
    color=[]
    chart_title=[]

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'btn_open_piechart' in changed_id:
        if list_of_names is not None:
            print(list_of_names)
            archivo = list_of_names
            with open(CHART_DIRECTORY+archivo) as file:
                data = json.load(file)
                for drop_values   in data['grafico']:
                    consulta = str(drop_values['consulta'])
                    datos_y1 = drop_values['datos_y1']
                    var_list = drop_values['var_list']
                    color = drop_values['color']
                    chart_title = drop_values['chart_title']
    return archivo, consulta, datos_y1, var_list, color, chart_title