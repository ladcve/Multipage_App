import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Row import Row
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash_table.Format import Format, Symbol
import dash_admin_components as dac
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
query = 'SELECT * FROM PRESION_ROCIO'
data_results =pd.read_sql(query, con)

#Listado de pozos activos
query = "SELECT NOMBRE FROM ITEMS WHERE ESTATUS=1 "
well_list =pd.read_sql(query, con)
#well_list = well_list.sort_values('NOMBRE')['NOMBRE'].unique()

con.close()

#Define las columans de la tabla y su formato


layout = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Card([
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        dbc.Button(html.Span(["filas ", html.I(className="fas fa-plus-circle ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                         id="btn_add_rocio", color="primary", n_clicks=0, className="mr-1"),
                    ], width={"size": 2, "offset": 1}),
                    dbc.Col([
                        dbc.Button(html.Span(["Grabar ", html.I(className="fas fa-save ml-1")],style={'font-size':'1.5em','text-align':'center'}), 
                        id="btn_save_rocio", color="success", n_clicks=0, className="mr-1"),
                    ], width={"size": 1, "offset": 1}),
                ]),
                html.Br(),
            ], style={"background-color": "#F9FCFC"},),
        ], width={"size": 3, "offset": 0}),
    ]),
    html.Br(),
    html.Div(id="save_messages_rocio"),
    html.Br(),
    dbc.Row([
        dac.Box([
                dac.BoxHeader(
                    collapsible = False,
                    closable = False,
                    title="PRESION DE ROCIO"
                ),
                dac.BoxBody(

                    dash_table.DataTable(
                        id='tb_rocio',
                        columns=[
                            {'id': 'NOMBRE', 'name': 'NOMBRE', 'presentation': 'dropdown'},
                            {'id': 'FECHA', 'name': 'FECHA', 'type':'datetime'},
                            {'id': 'PRESION', 'name': 'PRESION', 'type':'numeric'},
                            {'id': 'COMENTARIO', 'name': 'COMENTARIO', 'type':'text'},
                        ],
                        dropdown={
                            'NOMBRE': {
                                'options': [
                                    {'label': i, 'value': i}
                                    for i in well_list['NOMBRE'].unique()
                                ]
                            },
                        },
                        data=data_results.to_dict('records'),
                        editable=True,
                        style_header={
                            'backgroundColor': 'blue',
                            'fontWeight': 'bold',
                            'color': 'white'
                        },
                        filter_action="native",
                        sort_action="native",  # give user capability to sort columns
                        sort_mode="single",  # sort across 'multi' or 'single' columns
                        page_action="native",
                        row_deletable=True,
                        page_current= 0,
                        page_size= 13,
                        style_table={'height': '500px', 'overflowY': 'auto'},
                        style_cell={'textAlign': 'left', 'minWidth': '100px', 'width': '200px', 'maxWidth': '300px','font_size':'20px'},
                    ),

                ),	
            ],
            color='primary',
            solid_header=True,
            elevation=4,
            width=12
        ),
    ]),
    dbc.Modal(
        [
            dbc.ModalHeader("Datos guardados"),
        ],
        id="modal_rocio",
        is_open=False,
    ),
])

@app.callback(
    Output('tb_rocio', 'data'),
    Input('btn_add_rocio', 'n_clicks'),
    State('tb_rocio', 'data'),
    State('tb_rocio', 'columns'))
def add_unit(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows

@app.callback(
    Output("modal_rocio", "is_open"),
    Input("btn_save_rocio", "n_clicks"),
    [State('tb_rocio', 'data'),State('modal_rocio','is_open')]
)
def update_table_unitsvariables(n_clicks, dataset, is_open):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    mensaje = ''
    pg = pd.DataFrame(dataset)
    if 'btn_save_rocio' in changed_id:
        con = sqlite3.connect(archivo)
        pg.to_sql('PRESION_ROCIO', con, if_exists='replace', index=False)
        con.commit()
        con.close()
        is_open=True
    return is_open
