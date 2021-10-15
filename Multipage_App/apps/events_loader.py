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
query = 'SELECT * FROM EVENTOS'
data_results =pd.read_sql(query, con)
con.close()

layout = html.Div([
    dbc.Row([
        dbc.Col([
            dcc.Input(
                id='inp_add_columns',
                placeholder='Entre el nombre de columna',
                value='',
                style={'padding': 10}
            ),
        ], width=2),
        dbc.Col([
            dbc.Button("Agregar Columnas", id="btn_add_columns", color="primary", n_clicks=0, className="mr-1"),
        ], width=1.5),
        dbc.Col([
            dbc.Button("Agregar Filas", id="btn_add_row", color="primary", n_clicks=0, className="mr-1"),
        ], width=1),
        dbc.Col([
            dbc.Button("Salvar cambios", id="btn_save_change", color="success", n_clicks=0, className="mr-1"),
        ], width=1)
    ]),
    html.Br(),
    html.Div(id="save_message"),
    html.Br(),
    dbc.Row([
        dbc.Card([
            dbc.CardBody([
                dash_table.DataTable(
                    id='tab_data',
                    columns = [{'name': i, 'id': i} for i in data_results.columns],
                    data = data_results.to_dict('records'),
                        editable=True,
                        row_deletable=True,
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
])


@app.callback(
    Output('tab_data', 'data'),
    Input('btn_add_row', 'n_clicks'),
    State('tab_data', 'data'),
    State('tab_data', 'columns'))
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows


@app.callback(
    Output('tab_data', 'columns'),
    Input('btn_add_columns', 'n_clicks'),
    State('inp_add_columns', 'value'),
    State('tab_data', 'columns'))
def update_columns(n_clicks, value, existing_columns):
    if n_clicks > 0:
        existing_columns.append({
            'id': value, 'name': value,
            'renamable': True, 'deletable': True
        })
    return existing_columns

@app.callback(
    Output("save_message", "children"),
    Input("btn_save_change", "n_clicks"),
    [State('tab_data', 'data')]
)
def fupdate_table(n_clicks, dataset):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    mensaje = ''
    pg = pd.DataFrame(dataset)
    pg['FECHA'] = pd.to_datetime(pg['FECHA'])
    if 'btn_save_change' in changed_id:
        con = sqlite3.connect(archivo)
        pg.to_sql('EVENTOS', con, if_exists='replace', index=False)
        con.commit()
        con.close()
        mensaje='Datos guardados'
    return mensaje