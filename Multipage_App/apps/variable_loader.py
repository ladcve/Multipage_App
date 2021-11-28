import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Row import Row
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table
import sqlite3
import configparser
import sys
import os.path
from os import listdir
from os.path import isfile, join
import numpy as np
import pandas as pd
from datetime import date
from collections import OrderedDict
import base64
import os

from app import app 

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
query = 'SELECT * FROM VARIABLES'
data_results =pd.read_sql(query, con)
con.close()

#Listado de query
pathway = './querys'
files = [f for f in listdir(pathway) if isfile(join(pathway, f))]

file_name = ''

#Variable con la ruta para salvar los querys
QUERY_DIRECTORY = "./querys"


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
            dbc.Button("Agregar Variable", id="btn_add_var", color="primary", n_clicks=0, className="mr-1"),
        ], width=1),
        dbc.Col([
            dbc.Button("Salvar cambios", id="btn_save_var", color="success", n_clicks=0, className="mr-1"),
        ], width=1),
        dbc.Col([
            dbc.Button("Probar", id="btn_run_var", color="warning", n_clicks=0, className="mr-1"),
        ], width=1)
    ]),
    html.Br(),
    html.Div(id="save_message_var"),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.Label(['Variables Calculadas'],style={'font-weight': 'bold', "text-align": "left"})),
                dbc.CardBody([
                    dbc.Spinner(
                        dash_table.DataTable(
                            id='tab_variables',
                            columns = [{'name': i, 'id': i} for i in data_results.columns],
                            data = data_results.to_dict('records'),
                                editable=True,
                                filter_action="native",
                                style_header={
                                    'backgroundColor': 'blue',
                                    'fontWeight': 'bold',
                                    'color': 'white',
                                    'font-family':'arial'
                                },
                                sort_action="native",
                                sort_mode="multi",
                                row_selectable="single",
                                row_deletable=True,
                                selected_columns=[],
                                selected_rows=[],
                                page_current= 0,
                                page_size= 13,
                                style_table={'height': '500px', 'overflowY': 'auto'},
                                style_cell={'textAlign': 'left', 'minWidth': '100px', 'width': '200px', 'maxWidth': '300px', 'font-family':'arial'},
                        ),
                    ),
                ]),
            ]),
        ]),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.Label(['Resultados'],style={'font-weight': 'bold', "text-align": "left"})),
                dbc.CardBody([
                    dash_table.DataTable(
                        id='tab_resultados',
                            editable=False,
                            style_header={
                                'backgroundColor': 'blue',
                                'fontWeight': 'bold',
                                'color': 'white'
                            },
                            filter_action="native",
                            sort_action="native",  # give user capability to sort columns
                            sort_mode="single",  # sort across 'multi' or 'single' columns
                            page_action="native",
                            page_current= 0,
                            page_size= 13,
                            style_table={'height': '500px', 'overflowY': 'auto'},
                            style_cell={'textAlign': 'left', 'minWidth': '100px', 'width': '200px', 'maxWidth': '300px'},
                    ),
                ]),
            ]),
        ]),
    ]),
])


@app.callback(
    Output('tab_variables', 'data'),
    Input('btn_add_var', 'n_clicks'),
    State('tab_variables', 'data'),
    State('tab_variables', 'columns'))
def add_variable(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows


@app.callback(
    Output("save_message_var", "children"),
    Input("btn_save_var", "n_clicks"),
    [State('tab_variables', 'data')]
)
def update_table_variables(n_clicks, dataset):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    mensaje = ''
    pg = pd.DataFrame(dataset)
    if 'btn_save_var' in changed_id:
        con = sqlite3.connect(archivo)
        pg.to_sql('VARIABLES', con, if_exists='replace', index=False)
        con.commit()
        con.close()
        mensaje='Datos guardados'
    return mensaje

@app.callback(
    [Output("tab_resultados", "data"), Output("tab_resultados", "columns")],
    [Input("btn_run_var", "n_clicks"),
    Input('tab_variables', 'data'),
    Input('tab_variables', 'derived_virtual_selected_rows'),
    Input('dpd-query-lista', 'value')], 
    [State('tab_resultados', 'data'), State('tab_resultados', 'columns')]
)
def update_table_results(n_clicks, rows, row_id,file_name, data, columns):
    data_results = pd.DataFrame()
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    df = pd.DataFrame()

    if 'btn_run_var' in changed_id:
        indice = row_id[0]
        ecuacion = rows[indice]['ECUACION']
        titulo = rows[indice]['TITULO']
        con = sqlite3.connect(archivo)
        if file_name is not None:
            with open(os.path.join(QUERY_DIRECTORY, file_name)) as f:
                contenido = f.readlines()
                for linea in contenido:
                    query =  linea
                df =pd.read_sql(query, con)
            evalu = eval(ecuacion)
            df[titulo] = evalu 

    columns = [{'name': i, 'id': i, 'renamable': True, 'deletable': True} for i in df.columns]
    data = df.to_dict('records')
    return data, columns