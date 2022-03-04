import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Row import Row
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_admin_components as dac
import dash_table
import sqlite3
from matplotlib.pyplot import close
from sqlalchemy import create_engine
import configparser
import sys
import os.path
import os
import numpy as np
import pandas as pd
from datetime import date
from collections import OrderedDict
from queue import Queue
import time
import threading
import base64
import os
import pyodbc 

progress_queue = Queue(1)
progress_memeory = 0

from app import app 

#Lee el archivo de configuracion
configuracion = configparser.ConfigParser()

if os.path.isfile('config.ini'):

    configuracion.read('config.ini')

    if 'BasedeDatos' in configuracion:
        Origen = configuracion['BasedeDatos']['Origen']
        Catalogo = configuracion['BasedeDatos']['Catalogo']
        Password = configuracion['BasedeDatos']['Password']
        ruta = configuracion['BasedeDatos']['ruta']

    if 'items' in configuracion:
        items = configuracion['items']['consulta']

#Crea la BD de SQLite en la ruta establecida en el archivo de configuracion
basededatos = '\ProdAnalysis.db'
archivo = ruta +  basededatos        

con = sqlite3.connect(archivo)

#Extrae la maxima fecha de la BD para actualizar los a partir de dicha fecha
cursor = con.execute("SELECT MAX(FECHA) FROM CIERRE_DIARIO_POZO")
dstart = str(cursor.fetchall())
dstart = dstart.replace("[('","")
dstart = dstart.replace("',)]","")

con.close()

layout = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Card([
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        dbc.Button("Actualizar BD", id="btn_udpate_db", color="success", n_clicks=0, className="mr-1"),
                    ], width={"size": 2, "offset": 1}),
                    dbc.Col([
                        html.Label(['Fecha última Act. :'],style={'font-weight': 'bold', "text-align": "left"}),
                        html.Label(html.Div(id="txt-last-update"),style={'font-weight': 'bold', 'color':'blue', "text-align": "left", "margin-left": "15px"}),
                    ], width={"size": 5, "offset": 1})
                ]),
                html.Br(),
            ], style={"background-color": "#F9FCFC"},),
        ], width={"size": 4, "offset": 0}), 
    ]),
    html.Br(),
    dbc.Spinner(
        html.Div(id="save_db_messages"),
    ),
    dcc.ConfirmDialog(
        id='error-connect-pdms',
        message='Error al conectarse a PDMS. Por favor verifica el VPN.',
    ),
    dcc.ConfirmDialog(
        id='error-connect-sqlite',
        message='Error al actualizar las tablas',
    ),
    html.Br(),
    dbc.Row([
        dac.Box([
                dac.BoxHeader(
                    collapsible = False,
                    closable = False,
                    title="Tablas de la BD"
                ),
                dac.BoxBody([
                    dcc.Checklist(
                        id='ckl-tables',
                        options=[
                            {'label': ' Prod. Asignada', 'value': 'CIERRE'},
                            {'label': ' Prod. Estimada', 'value': 'ESTIM'},
                            {'label': ' Lecturas de Pozos', 'value': 'LECTU'},
                            {'label': ' Potencial de Pozos', 'value': 'POTEN'},
                            {'label': ' Pruebas de Pozos', 'value': 'PRUEBAS'},
                            {'label': ' Perdidas de Prod.', 'value': 'PERDI'},
                        ],
                        value=['LECTU', 'CIERRE', 'ESTIM','POTEN','PRUEBAS','PERDI']
                    ),
                ]),	
            ],
            color='primary',
            solid_header=True,
            elevation=4,
            width=4
        ),
    ]),
    dbc.Modal(
        [
            dbc.ModalHeader("BD Actualizada"),
        ],
        id="modal_db_update",
        is_open=False,
    ),
])

@app.callback(
    [Output('modal_db_update', 'is_open'),
     Output('txt-last-update', 'children'),
     Output('error-connect-pdms', 'displayed'),
     Output('error-connect-sqlite', 'displayed')
     ],
    [Input('btn_udpate_db', 'n_clicks'),
    Input('ckl-tables', 'value'),
    State('modal_db_update','is_open')],
    )
def add_items_rows(n_clicks, tables_selected, is_open):

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    mensaje=''
    sqlite_table = ''
    error_pdms = False
    error_sqlite = False
    i=1
    
    #Obtiene ultima fecha de la BD
    con = sqlite3.connect(archivo)
    query = "SELECT MAX(FECHA) FROM CIERRE_DIARIO_POZO"
    temp=pd.read_sql(query, con)
    last_update = temp.iloc[0]['MAX(FECHA)']
    con.close()

    if 'btn_udpate_db' in changed_id:
        for tabla in tables_selected:
            con = sqlite3.connect(archivo)
            try:
                try:
                    SQLPd=pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+Origen+';DATABASE='+Catalogo+';UID=pdmsadm;PWD='+ Password)
                except:
                    error_pdms = True

                if tabla=="CIERRE" and error_pdms is False:
                    #Leyendo los datos de produccion fiscal
                    read_fiscal = configuracion['fiscal']['consulta']
                    sqlite_table = "CIERRE_DIARIO_POZO"
                    df_fiscal=pd.read_sql_query(read_fiscal.format(dstart),SQLPd)
                    df_fiscal.to_sql(sqlite_table, con, if_exists='replace')

                if tabla=="ESTIM" and error_pdms is False:
                    read_estimaciones = configuracion['estimaciones']['consulta']
                    sqlite_table = "ESTIMACIONES_POZO"
                    df_estimaciones=pd.read_sql_query(read_estimaciones.format(dstart),SQLPd)
                    df_estimaciones.to_sql(sqlite_table, con, if_exists='append')
                if tabla =="LECTU" and error_pdms is False:
                    read_lecturas = configuracion['lecturas']['consulta']
                    sqlite_table = "LECTURAS_POZO"
                    df_lecturas=pd.read_sql_query(read_lecturas.format(dstart),SQLPd)
                    df_lecturas.to_sql(sqlite_table, con, if_exists='replace')
                if tabla =="POTEN" and error_pdms is False:
                    read_potencial = configuracion['potencial']['consulta']
                    sqlite_table = "POTENCIAL_POZO"
                    df_potencial=pd.read_sql_query(read_potencial.format(dstart),SQLPd)
                    df_potencial.to_sql(sqlite_table, con, if_exists='replace')
                if tabla == "PRUEBAS" and error_pdms is False:
                    read_pruebas = configuracion['pruebas']['consulta']
                    sqlite_table = "PRUEBAS_POZO"
                    df_pruebas=pd.read_sql_query(read_pruebas.format(dstart),SQLPd)
                    df_pruebas.to_sql(sqlite_table, con, if_exists='replace')
 
                is_open = True
                con.commit()

                temp=pd.read_sql(query, con)
                last_update = temp.iloc[0]['MAX(FECHA)']
                con.close()
                i += 1
            except Exception as e:
                print('ERROR: %s',e)
                mensaje = e
                error_sqlite = True

    return is_open, last_update, error_pdms, error_sqlite