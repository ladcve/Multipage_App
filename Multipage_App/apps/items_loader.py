import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Row import Row
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash_html_components.Br import Br
import dash_table
import sqlite3
from sqlalchemy import create_engine
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
engine = create_engine('sqlite:///'+archivo, echo=True)
con = engine.connect()
#con = sqlite3.connect(archivo)

#Listado de pozos activos
query = 'SELECT * FROM ITEMS'
data_results =pd.read_sql(query, con)
con.close()

layout = html.Div([
     dbc.Row([
        dbc.Col([
            dbc.Button("Agregar Filas", id="btn_add_items", color="primary", n_clicks=0, className="mr-1"),
        ], width=1),
        dbc.Col([
            dbc.Button("Salvar cambios", id="btn_save_items", color="success", n_clicks=0, className="mr-1"),
        ], width=1)
    ]),
    html.Br(),
    html.Div(id="save_item_messages"),
    html.Br(),
    dbc.Row([
        dbc.Card([
            dbc.CardBody([
                dash_table.DataTable(
                    id='table-items',
                    data=data_results.to_dict('records'),
                    columns = [{'name': i, 'id': i} for i in data_results.columns],
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
            ])
        ])
    ]),
    html.Div(id='table-items-container')
])

@app.callback(
    Output('table-items', 'data'),
    Input('btn_add_items', 'n_clicks'),
    State('table-items', 'data'),
    State('table-items', 'columns'))
def add_items_rows(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows

@app.callback(
    Output("save_item_messages", "children"),
    Input("btn_save_items", "n_clicks"),
    [State('table-items', 'data')]
)
def update_table_item(n_clicks, dataset):
    mensaje = ''
    pg = pd.DataFrame(dataset)
    pg["GRADIENTE"] = pd.to_numeric(pg["GRADIENTE"])
    pg["PROF_TOTAL"] = pd.to_numeric(pg["PROF_TOTAL"])
    pg["XCOOR_FONDO"] = pd.to_numeric(pg["XCOOR_FONDO"])
    pg["YCOOR_FONDO"] = pd.to_numeric(pg["YCOOR_FONDO"])
    if n_clicks > 0:
        con = engine.connect()
        #con = sqlite3.connect(archivo)
        pg.to_sql('ITEMS', con, if_exists='replace', index=False)
        #con.commit()
        con.close()
        mensaje='Datos guardados'
    return mensaje