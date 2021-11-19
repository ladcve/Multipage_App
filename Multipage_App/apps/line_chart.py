import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Row import Row
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash_html_components.Br import Br
import plotly.graph_objects as go
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

#Listado de eventos
query = "SELECT * FROM EVENTOS"
event_list =pd.read_sql(query, con)

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
                            clearable=False,
                            multi=True
                        ),
                    ], width={"size": 4, "offset": 0}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button("Mostrar Grafico", id="btn_show_chart", color="success", className="mr-3"),
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
                        dbc.Input(id="inp-ruta-linechart", placeholder="Type something...", type="text", style={'backgroundColor':'white'}),
                    ], width={"size": 3, "offset": 1}),
                     dbc.Col([
                        html.Br(),
                        dcc.Upload(
                            dbc.Button("Cargar Template", n_clicks=0, color="warning", className="mr-3"),
                            id='btn_open_linechart',
                            multiple=False
                        ),
                    ], width={"size": 3, "offset": 0}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button("Grabar Template", id="btn_save_linechart", n_clicks=0, color="warning", className="mr-3"),
                        html.Div(id="save_message_linechart"),
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
                dbc.CardHeader(html.Label(['Gráfico de Líneas'],style={'font-weight': 'bold', "text-align": "left"})),
                dbc.CardBody([
                    dbc.Spinner(
                        dcc.Graph(id='cht-line-chart'),
                    ),
                ])
            ]),
        ], width=9),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.Label(['Opciones'],style={'font-weight': 'bold', "text-align": "left"})),
                dbc.CardBody([
                    dbc.Card([
                        dbc.CardHeader(html.Label(['Eje Primario'],style={'font-weight': 'bold', "text-align": "left"})),
                        dbc.CardBody([
                            html.Label(['Datos:'],style={'font-weight': 'bold', "text-align": "left"}),
                            dcc.Dropdown(
                                id='dpd-column-list-y1',
                                clearable=False,
                                multi=True
                            ),
                        ]),
                    ]),
                    dbc.Card([
                        dbc.CardHeader(html.Label(['Eje Secundario'],style={'font-weight': 'bold', "text-align": "left"})),
                        dbc.CardBody([
                            html.Label(['Datos:'],style={'font-weight': 'bold', "text-align": "left"}),
                            dcc.Dropdown(
                                id='dpd-column-list-y2',
                                clearable=False,
                                multi=True
                            ),
                        ]),
                    ]),
                    html.Br(),
                    dbc.Card([
                        dbc.CardHeader(html.Label(['Eventos'],style={'font-weight': 'bold', "text-align": "left"})),
                        dbc.CardBody([
                            daq.ToggleSwitch(
                                id='ts-annotation',
                                value=False,
                                label='Mostrar Anotaciones',
                                labelPosition='top'
                            ),
                            dash_table.DataTable(id="dt_table_event", 
                                columns = [{'name': i, 'id': i, "deletable": True} for i in event_list.columns],
                                data = event_list.to_dict('records'),
                                style_as_list_view=True,
                                style_cell={'padding': '5px'},
                                style_table={
                                    'overflowX': 'auto',
                                    'whiteSpace': 'normal',
                                    'height': 'auto',
                                },
                                style_header={
                                    'backgroundColor': 'blue',
                                    'fontWeight': 'bold',
                                    'color': 'white',

                                },),
                        ]),
                    ]),
                ])
            ]),
        ], width=3),
    ]),
])

@app.callback(
    Output('cht-line-chart','figure'),
    [Input("btn_show_chart", "n_clicks"),
     Input('dpd-consulta-lista', 'value'), 
     Input('dpd-pozo-lista', 'value'),
     Input('dpd-column-list-y1', 'value'),
     Input('dpd-column-list-y2', 'value'),
     Input('ts-annotation', 'value'), 
     Input('dt_table_event', 'data')])
def update_line_chart(n_clicks, file_name, well_name, column_list_y1, column_list_y2, show_annot, annot_data):

    data_results = pd.DataFrame()
    quer= ''
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    if 'btn_show_chart' in changed_id:
        con = sqlite3.connect(archivo)
        if file_name is not None:
            with open(os.path.join(QUERY_DIRECTORY, file_name)) as f:
                contenido = f.readlines()
            if contenido is not None:
                for linea in contenido:
                    query =  linea +" ORDER BY FECHA"
                data_results =pd.read_sql(query, con)
                data_results = data_results[data_results['NOMBRE'].isin(well_name)]
                i=1
                for columnas_y1 in column_list_y1:
                    fig.add_trace(
                        go.Scatter(x=data_results['FECHA'],
                            y=data_results[columnas_y1],
                            name=columnas_y1,
                            yaxis= 'y'+ str(i)),
                        secondary_y=False,
                    )
                    i=+1
                    yaxis4=dict(
                        title="yaxis4 title",
                        titlefont=dict(
                            color="#9467bd"
                        ),
                        tickfont=dict(
                            color="#9467bd"
                        ),
                        anchor="free",
                        overlaying="y",
                        side="right",
                        position=0.85
                    )
                for columnas_y2 in column_list_y2:
                    fig.add_trace(
                        go.Scatter(x=data_results['FECHA'],
                            y=data_results[columnas_y2],
                            name=columnas_y2,
                            yaxis= 'y'+ str(i)),
                        secondary_y=True,
                    )
                    i=+1
                fig.update_xaxes(title_text="Fecha")
                fig.update_layout(
                    autosize=False,
                    width=1400,
                    height=780,
                    margin=dict(
                        l=50,
                        r=50,
                        b=100,
                        t=100,
                        pad=4
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
                if show_annot:
                    dff = pd.DataFrame(annot_data)
                    for ind in dff.index:
                        fig.add_annotation(x=dff['FECHA'][ind], y=5,
                            text=dff['EVENTO'][ind],
                            showarrow=False,
                            textangle=-90,
                            arrowhead=1)
        con.close()
    return fig

@app.callback(
    [Output('dpd-column-list-y1','options'),
     Output('dpd-column-list-y2','options')],
    [Input('dpd-consulta-lista', 'value')])
def update_column_list(file_name):

    data_results = pd.DataFrame()
    columns = [{'label': i, 'value': i} for i in []]
    quer= ''
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'dpd-consulta-lista' in changed_id:
        con = sqlite3.connect(archivo)
        if file_name:
            with open(os.path.join(QUERY_DIRECTORY, file_name)) as f:
                contenido = f.readlines()
                for linea in contenido:
                    query =  linea
                data_results =pd.read_sql(query, con)
                columns = [{'label': i, 'value': i} for i in data_results.columns]
        con.close()

    return columns, columns

@app.callback(
    Output('save_message_linechart','children'),
    [Input('btn_save_linechart', 'n_clicks'),
    Input('dpd-consulta-lista', 'value'),
    Input('dpd-column-list-y1', 'value'),
    Input('dpd-column-list-y2', 'value'),
    Input('inp-ruta-linechart', 'value')]) 
def save_linechart(n_clicks, consulta, datos_y1, datos_y2, file_name ):
    mensaje=''
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'btn_save_linechart' in changed_id:
        data = {}
        data['grafico'] = []
        data['grafico'].append({
            'consulta': consulta,
            'datos_y1': datos_y1,
            'datos_y2': datos_y2})
        with open(CHART_DIRECTORY+file_name, 'w') as file:
            json.dump(data, file, indent=4)
        mensaje = 'Archivo guardado'
    return mensaje

@app.callback( [Output('inp-ruta-linechart', 'value'),
                Output('dpd-consulta-lista', 'value'),
                Output('dpd-column-list-y1', 'value'),
                Output('dpd-column-list-y2', 'value'),],
              [Input('btn_open_linechart', 'filename'),
              Input('btn_open_linechart', 'contents')]
              )
def open_linechart( list_of_names, list_of_contents):
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
    return archivo, consulta, datos_y1, datos_y2