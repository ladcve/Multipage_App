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

#Listado de pozos activos
query = "SELECT NOMBRE FROM ITEMS WHERE ESTATUS=1 "
well_list =pd.read_sql(query, con)
well_list = well_list.sort_values('NOMBRE')['NOMBRE'].unique()


query = 'SELECT * FROM WELLBORE'
data_results =pd.read_sql(query, con)
con.close()

layout = html.Div([
     dbc.Row([
        dbc.Col([
            dbc.Button("Agregar Filas", id="btn_add_rows", color="primary", n_clicks=0, className="mr-1"),
        ], width=1),
        dbc.Col([
            dbc.Button("Salvar cambios", id="btn_save_data_changes", color="success", n_clicks=0, className="mr-1"),
        ], width=1)
    ]),
    html.Br(),
    html.Div(id="save_data_messages"),
    html.Br(),
    dbc.Row([
        dbc.Card([
            dbc.CardBody([
                dash_table.DataTable(
                    id='table-dropdown',
                    data=data_results.to_dict('records'),
                    columns=[
                                {'id': 'NOMBRE', 'name': 'NOMBRE', 'presentation': 'dropdown'},
                                {'id': 'TIPO', 'name': 'TIPO', 'presentation': 'dropdown'},
                                {'id': 'DESCRIPCION', 'name': 'DESCRIPCION'},
                                {'id': 'ID', 'name': 'ID'},
                                {'id': 'OD', 'name': 'OD'},
                                {'id': 'MD', 'name': 'MD'},
                                {'id': 'LONGITUD', 'name': 'LONGITUD'},
                            ],

                    editable=True,
                    dropdown = {
                        'NOMBRE': {
                            'options': [
                                {'label': i, 'value': i}
                                for i in  well_list
                            ]
                        },
                        'TIPO': {    
                            'options': [
                                {'label': 'Arbol Navidad', 'value': 'XMAST'},
                                {'label': 'Valvula Seguridad', 'value': 'SAFEV'},
                                {'label': 'Tubbing', 'value': 'TUBIN'},
                                {'label': 'Casing 13 3/8', 'value': 'CASIN13'},
                                {'label': 'Casing 12', 'value': 'CASIN12'},
                                {'label': 'Cementacion', 'value': 'CEMEN'},
                                {'label': 'Perforaciones', 'value': 'PERF'},
                            ],
                        }
                    },
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
    html.Div(id='table-dropdown-container')
])

@app.callback(
    Output('table-dropdown', 'data'),
    Input('btn_add_rows', 'n_clicks'),
    State('table-dropdown', 'data'),
    State('table-dropdown', 'columns'))
def add_rows(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows

@app.callback(
    Output("save_data_messages", "children"),
    Input("btn_save_data_changes", "n_clicks"),
    [State('table-dropdown', 'data')]
)
def fupdate_table_wellbore(n_clicks, dataset):
    mensaje = ''
    pg = pd.DataFrame(dataset)

    if n_clicks > 0:
        con = sqlite3.connect(archivo)
        pg.to_sql('WELLBORE', con, if_exists='replace', index=False)
        con.commit()
        con.close()
        mensaje='Datos guardados'
    return mensaje