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
query = 'SELECT * FROM MARCADORES'
data_results =pd.read_sql(query, con)
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
                         id="btn_add_rows", color="primary", n_clicks=0, className="mr-1"),
                    ], width={"size": 2, "offset": 1}),
                    dbc.Col([
                        dbc.Button(html.Span(["Grabar ", html.I(className="fas fa-save ml-1")],style={'font-size':'1.5em','text-align':'center'}), 
                        id="btn_save_changes", color="success", n_clicks=0, className="mr-1"),
                    ], width={"size": 1, "offset": 1}),
                ]),
                html.Br(),
            ]),
        ], width={"size": 3, "offset": 0}),
    ]),
    html.Br(),
    html.Div(id="save_messages"),
    html.Br(),
    dbc.Row([
        dac.Box([
                dac.BoxHeader(
                    collapsible = False,
                    closable = False,
                    title="Marcadores Estratgráficos"
                ),
                dac.BoxBody(
                    dash_table.DataTable(
                        id='tab_data_markers',
                        data = data_results.to_dict('records'),
                        columns = [
                            dict(id='NOMBRE', name='NOMBRE', type='text'), 
                            dict(id='FORMACION', name='FORMACION', type='text'), 
                            dict(id='MD', name=u'MD (ft)', type='numeric', 
                            format= Format(
                                        precision=6,
                                        symbol=Symbol.yes,
                                        symbol_suffix=u' ft'
                                    )
                            ), 
                            dict(id='TVD', name=u'TVD (ft)', type='numeric', 
                            format= Format(
                                        precision=6,
                                        symbol=Symbol.yes,
                                        symbol_suffix=u' ft'
                                    )
                            ),
                            dict(id='ESPESOR', name=u'ESPESOR (ft)', type='numeric', 
                            format= Format(
                                        precision=6,
                                        symbol=Symbol.yes,
                                        symbol_suffix=u' ft'
                                    )
                            ),
                            dict(id='TIPO', name='TIPO', type='text'), 
                        ],
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
                        page_size= 20,
                        style_table={'height': '500px', 'overflowY': 'auto'},
                        style_cell={'textAlign': 'left', 'minWidth': '100px', 'width': '200px', 'maxWidth': '300px'},
                        style_cell_conditional=[
                            {
                                'if': {'column_id': c},
                                'textAlign': 'right'
                            } for c in ['MD', 'TVD', 'ESPESOR']
                        ],
                    ),
                ),	
            ],
            color='primary',
            solid_header=True,
            elevation=4,
            width=12
        ),
    ]),
])


@app.callback(
    Output('tab_data_markers', 'data'),
    Input('btn_add_rows', 'n_clicks'),
    State('tab_data_markers', 'data'),
    State('tab_data_markers', 'columns'))
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows


@app.callback(
    Output("save_messages", "children"),
    Input("btn_save_changes", "n_clicks"),
    [State('tab_data_markers', 'data')]
)
def fupdate_table(n_clicks, dataset):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    mensaje = ''
    pg = pd.DataFrame(dataset)
    if 'btn_save_change' in changed_id:
        con = sqlite3.connect(archivo)
        pg.to_sql('MARCADORES', con, if_exists='replace', index=False)
        con.commit()
        con.close()
        mensaje='Datos guardados'
    return mensaje