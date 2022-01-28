import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Row import Row
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_admin_components as dac
from dash_table.Format import Format, Symbol
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
engine = create_engine('sqlite:///'+archivo, echo=False)
con = engine.connect()
#con = sqlite3.connect(archivo)

#Listado de pozos activos
query = 'SELECT * FROM ITEMS'
data_results =pd.read_sql(query, con)
con.close()

layout = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Card([
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        dbc.Button(html.Span(["Filas", html.I(className="fas fa-plus-circle ml-1")],style={'font-size':'1.5em','text-align':'center'}), 
                        id="btn_add_items", color="primary", n_clicks=0, className="mr-1"),
                    ], width={"size": 2, "offset": 1}),
                    dbc.Col([
                        dbc.Button(html.Span(["Grabar", html.I(className="fas fa-save ml-1")],style={'font-size':'1.5em','text-align':'center'}), 
                        id="btn_save_items", color="success", n_clicks=0, className="mr-1"),
                    ], width={"size": 1, "offset": 1})
                ]),
                html.Br(),
            ], style={"background-color": "#F9FCFC"},),
        ], width={"size": 3, "offset": 0}),
     ]),
    html.Br(),
    html.Div(id="save_item_messages"),
    html.Br(),
    dbc.Row([
        dac.Box([
                dac.BoxHeader(
                    collapsible = False,
                    closable = False,
                    title="Listado de Items"
                ),
                dac.BoxBody(
                    dash_table.DataTable(
                        id='table-items',
                        data=data_results.to_dict('records'),
                        columns = [
                            dict(id='NOMBRE', name='NOMBRE', type='text'), 
                            dict(id='FLUIDO', name='FLUIDO', type='text'), 
                            dict(id='FUNCION', name='FUNCION', type='text'), 
                            dict(id='XCOORD', name='XCOORD', type='text'), 
                            dict(id='FECHA_CREACION', name='FECHA_CREACION', type='datetime'), 
                            dict(id='ESTATUS', name='ESTATUS', type='numeric', 
                            format= Format(
                                        precision=1
                                    )
                            ), 
                            dict(id='FECHA_PROD', name='FECHA_PROD', type='datetime'),
                            dict(id='METODO', name='METODO', type='text'),  
                            dict(id='CAMPO', name='CAMPO', type='text'),  
                            dict(id='YACIMIENTO', name='YACIMIENTO', type='text'),  
                            dict(id='PROF_TOTAL', name=u'PROF_TOTAL (ft)', type='numeric', 
                            format= Format(
                                        precision=6,
                                        symbol=Symbol.yes,
                                        symbol_suffix=u' ft'
                                    )
                            ),
                            dict(id='XCOOR_FONDO', name='XCOOR_FONDO', type='text'),  
                            dict(id='YCOOR_FONDO', name='YCOOR_FONDO', type='text'),
                            dict(id='GRADIENTE', name='GRADIENTE', type='numeric', 
                            format= Format(
                                        precision=6,
                                    )
                            ),
                            dict(id='PRES_HIDRO', name=u'PRES. HIDRO  (psig)', type='numeric', 
                            format= Format(
                                        precision=6,
                                        symbol=Symbol.yes,
                                        symbol_suffix=u' psig'
                                    )
                            ),
                            dict(id='PRES_CARGA', name=u'PRES. CARGA  (psig)', type='numeric', 
                            format= Format(
                                        precision=6,
                                        symbol=Symbol.yes,
                                        symbol_suffix=u' psig'
                                    )
                            ),
                            dict(id='PRES_PORO', name=u'PRES. PORO  (psig)', type='numeric', 
                            format= Format(
                                        precision=6,
                                        symbol=Symbol.yes,
                                        symbol_suffix=u' psig'
                                    )
                            ),
                            dict(id='GRAD_FRACT', name=u'GRAD. FRACT ', type='numeric', 
                            format= Format(
                                        precision=6,
                                    )
                            ),
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
                        page_size= 13,
                        style_table={'height': '500px', 'overflowY': 'auto'},
                        style_cell={'textAlign': 'left', 'minWidth': '100px', 'width': '200px', 'maxWidth': '300px'},
                    ),
                ),	
            ],
            color='primary',
            solid_header=True,
            elevation=4,
            width=12
        ),
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