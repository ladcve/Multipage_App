import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Row import Row
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash_html_components.Br import Br
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
TEMPLATE_DIRECTORY = "./template/"

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
                html.Label(['Consulta:'],style={'font-weight': 'bold', "text-align": "left"}),
                dcc.Dropdown(
                    id='dpd-query-lista',
                    options=[
                        {'label': i, 'value': i} for i in files
                    ],
                    clearable=False
                ),
            ], width=2),
            dbc.Col([
                html.Label(['Pozo:'],style={'font-weight': 'bold', "text-align": "left"}),
                dcc.Dropdown(
                    id='dpd-well-lista',
                    options=[{'label': i, 'value': i} for i in well_list],
                    clearable=False
                ),
            ], width=1),
            dbc.Col([
                html.Br(),
                dbc.Button("Ejecutar Reporte", id="btn_execute_report", color="success", className="mr-3"),
            ]),
            dbc.Col([
                html.Br(),
                dbc.Button("Exportar Excel", id="btn_export_excel", color="warning", className="mr-3"),
            ]),
            dbc.Col([
                html.Label(['Nombre Archivo:'],style={'font-weight': 'bold', "text-align": "left"}),
                dbc.Input(id="inp-ruta-report", placeholder="Type something...", type="text", style={'backgroundColor':'white'}),
            ], width={"size": 3, "offset": 1}),
            dbc.Col([
                html.Br(),
                dbc.Button("Salvar Reporte", id="btn_save_report", color="warning", className="mr-3"),
                html.Div(id="save_message_reporte"),
            ]),
            dbc.Col([
                html.Br(),
                dcc.Upload(
                    dbc.Button("Abrir Reporte",  color="warning", className="mr-3"),
                    id="btn_open_report",
                    multiple=False
                ),
            ]),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.Label(['Reporte'],style={'font-weight': 'bold', "text-align": "left"})),
                dbc.CardBody([
                    dbc.Spinner(
                        dash_table.DataTable(id="dt_report_results", 
                        style_as_list_view=True,
                        style_cell={'padding': '5px'},
                        style_header={
                            'backgroundColor': 'blue',
                            'fontWeight': 'bold',
                            'color': 'white'
                        },
                        style_table={'overflowX': 'auto'},
                        editable=False,
                        filter_action="native",
                        sort_action="native",
                        sort_mode="multi",
                        column_selectable="single",
                        page_action="native",
                        page_current= 0,
                        page_size= 20,),
                    ),
                ])
            ]),
        ], width=9),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.Label(['Opciones'],style={'font-weight': 'bold', "text-align": "left"})),
                dbc.CardBody([
                    html.Label(['Variable Calculadas:'],style={'font-weight': 'bold', "text-align": "left"}),
                    dcc.Dropdown(
                        id='dpd-var-list',
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
    [Output("dt_report_results", "data"), Output("dt_report_results", "columns")],
    [Input("btn_execute_report", "n_clicks"),
     Input('dpd-query-lista', 'value'), 
     Input('dpd-well-lista', 'value'),
     Input('dpd-var-list', 'value')],
    [State('dt_report_results', 'data'), State('dt_report_results', 'columns')]
)
def update_table(n_clicks, file_name, well_name, var_list, data, columns):
    df = pd.DataFrame()
    quer= ''
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

    if 'btn_execute_report' in changed_id:
        con = sqlite3.connect(archivo)
        query = "SELECT * FROM VARIABLES"
        variables =pd.read_sql(query, con)
        if file_name is not None:
            with open(os.path.join(QUERY_DIRECTORY, file_name)) as f:
                contenido = f.readlines()
            if contenido is not None:
                if well_name is not None:
                    for linea in contenido:
                        query =  linea + " WHERE NOMBRE='"+well_name+"'"
                else:
                    for linea in contenido:
                        query =  linea
                df =pd.read_sql(query, con)
            if var_list is not None:
                for var in var_list:
                    selec_var=variables.loc[variables['NOMBRE']==var]
                    ecuacion = selec_var.iloc[0]['ECUACION']
                    titulo = selec_var.iloc[0]['TITULO']
                    evalu = eval(ecuacion)
                    df[titulo] = evalu

    columns = [{'name': i, 'id': i, "deletable": True} for i in df.columns]
    data = df.to_dict('records')
    return data, columns

@app.callback(
    Output('save_message_reporte','children'),
    [Input('btn_save_report', 'n_clicks'),
    Input('dpd-query-lista', 'value'),
    Input('inp-ruta-report', 'value'),
    Input('dpd-var-list', 'value')]) 
def save_reporte(n_clicks, consulta, file_name, var_list ):
    mensaje=''
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'btn_save_report' in changed_id:
        data = {}
        data['reporte'] = []
        data['reporte'].append({
            'consulta': consulta,
            'var_list': var_list})
        with open(TEMPLATE_DIRECTORY+file_name, 'w') as file:
            json.dump(data, file, indent=4)
        mensaje = 'Archivo guardado'
    return mensaje

@app.callback( [Output('inp-ruta-report', 'value'),
                Output('dpd-query-lista', 'value'),
                Output('dpd-var-list', 'value')],
              [Input('btn_open_report', 'filename'),
              Input('btn_open_report', 'contents')]
              )
def open_report( list_of_names, list_of_contents):
    archivo = list_of_names
    consulta=[]
    var_list=[]

    if list_of_names is not None:
        print(list_of_names)
        archivo = list_of_names
        with open(TEMPLATE_DIRECTORY+archivo) as file:
            data = json.load(file)
            for drop_values   in data['reporte']:
                consulta = str(drop_values['consulta'])
                var_list = drop_values['var_list']
    return archivo, consulta, var_list