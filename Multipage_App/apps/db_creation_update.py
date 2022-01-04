import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Row import Row
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_admin_components as dac
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
                        dbc.Button("Crear BD", id="btn_create_db", color="primary", n_clicks=0, className="mr-1"),
                    ], width={"size": 3, "offset": 0}),
                    dbc.Col([
                        dbc.Button("Actualizar BD", id="btn_udpate_db", color="success", n_clicks=0, className="mr-1"),
                    ], width={"size": 2, "offset": 0})
                ]),
                html.Br(),
            ]),
        ], width={"size": 3, "offset": 0}), 
    ]),
    html.Br(),
    dbc.Spinner(
        html.Div(id="save_db_messages"),
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
                            {'label': ' Items', 'value': 'ITEMS'},
                            {'label': ' Asignada', 'value': 'CIERRE'},
                            {'label': ' Estimacion', 'value': 'ESTIM'},
                            {'label': ' Lecturas', 'value': 'LECTU'},
                            {'label': ' Potencial', 'value': 'POTEN'},
                            {'label': ' Pruebas', 'value': 'PRUEBAS'},
                            {'label': ' Perdidas', 'value': 'PERDI'},
                            {'label': ' Survey', 'value': 'SURVEY'},
                            {'label': ' Nodal', 'value': 'NODAL'},
                            {'label': ' Eventos', 'value': 'EVENTO'},
                            {'label': ' Wellbore', 'value': 'WELLB'},
                        ],
                        value=['ITEMS', 'CIERRE', 'ESTIM']
                    ),
                ]),	
            ],
            color='primary',
            solid_header=True,
            elevation=4,
            width=4
        ),
    ]),
])

@app.callback(
    Output('save_db_messages', 'children'),
    Input('btn_create_db', 'n_clicks'),
    Input('btn_udpate_db', 'n_clicks'),
    Input('ckl-tables', 'value'),)
def add_items_rows(n_clic_create, n_clic_update, tables_selected):

    input_id = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
    mensaje=''
    sqlite_table = ''
    i=1
    if n_clic_create>0 or n_clic_update>0:
        for tabla in tables_selected:
            con = sqlite3.connect(archivo)
            try:
                SQLPd=pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+Origen+';DATABASE='+Catalogo+';UID=pdmsadm;PWD='+ Password)
                print("Conexion exitosa a la BD: "+ Origen)

                if tabla =="ITEMS":
                    #Leyendo los datos de Items
                    df_items=pd.read_sql_query(items,SQLPd)
                    sqlite_table = "ITEMS"
                    df_items.to_sql(sqlite_table, con, if_exists='replace')
                if tabla=="CIERRE":
                    #Leyendo los datos de produccion fiscal
                    read_fiscal = configuracion['fiscal']['read']
                    fiscal = configuracion['fiscal']['consulta']
                    sqlite_table = "CIERRE_DIARIO_POZO"
                    if "btn_create_db" in input_id:
                        df_fiscal=pd.read_sql_query(fiscal,SQLPd)
                        df_fiscal.to_sql(sqlite_table, con, if_exists='replace')
                    if "btn_udpate_db" in input_id:
                        df_fiscal=pd.read_sql_query(read_fiscal.format(dstart),SQLPd)
                        df_fiscal.to_sql(sqlite_table, con, if_exists='append')
                    sqlite_table = "CIERRE_DIARIO_POZO"
                if tabla=="ESTIM":
                    read_estimaciones = configuracion['estimaciones']['read']
                    estimaciones = configuracion['estimaciones']['consulta']
                    sqlite_table = "ESTIMACIONES_POZO"
                    #Leyendo los datos de estimaciones de produccion
                    if "btn_create_db" in input_id:
                        df_estimaciones=pd.read_sql_query(estimaciones,SQLPd)
                        df_estimaciones.to_sql(sqlite_table, con, if_exists='replace')
                    if "btn_udpate_db" in input_id:
                        df_estimaciones=pd.read_sql_query(read_estimaciones.format(dstart),SQLPd)
                        df_estimaciones.to_sql(sqlite_table, con, if_exists='append')
                    sqlite_table = "ESTIMACIONES_POZO"
                if tabla =="LECTU":
                    read_lecturas = configuracion['lecturas']['read']
                    lecturas = configuracion['lecturas']['consulta']
                    sqlite_table = "LECTURAS_POZO"
                    #Leyendo los datos de lecturas
                    if "btn_create_db" in input_id:
                        df_lecturas=pd.read_sql_query(lecturas,SQLPd)
                        df_lecturas.to_sql(sqlite_table, con, if_exists='replace')
                    if "btn_udpate_db" in input_id:
                        df_lecturas=pd.read_sql_query(read_lecturas.format(dstart),SQLPd)
                        df_lecturas.to_sql(sqlite_table, con, if_exists='append')
                    sqlite_table = "LECTURAS_POZO"
                if tabla =="POTEN":
                    read_potencial = configuracion['potencial']['read']
                    potencial = configuracion['potencial']['consulta']
                    sqlite_table = "POTENCIAL_POZO"
                    #Leyendo los datos de potencial
                    if "btn_create_db" in input_id:
                        df_potencial=pd.read_sql_query(potencial,SQLPd)
                        df_potencial.to_sql(sqlite_table, con, if_exists='replace')
                    if "btn_udpate_db" in input_id:
                        df_potencial=pd.read_sql_query(read_potencial.format(dstart),SQLPd)
                        df_potencial.to_sql(sqlite_table, con, if_exists='append')
                    sqlite_table = "POTENCIAL_POZO"
                if tabla == "PRUEBAS":
                    read_pruebas = configuracion['pruebas']['read']
                    pruebas = configuracion['pruebas']['consulta']
                    sqlite_table = "PRUEBAS_POZO"
                    #Leyendo los datos de pruebas
                    if "btn_create_db" in input_id:
                        df_pruebas=pd.read_sql_query(pruebas,SQLPd)
                        df_pruebas.to_sql(sqlite_table, con, if_exists='replace')
                    if "btn_udpate_db" in input_id:
                        df_pruebas=pd.read_sql_query(read_pruebas.format(dstart),SQLPd)
                        df_pruebas.to_sql(sqlite_table, con, if_exists='append')
                    sqlite_table = "PRUEBAS_POZO"
                if tabla=="NODAL":
                    # tabla de analisis nodal
                    con.execute('''CREATE TABLE IF NOT EXISTS NODAL
                                (NOMBRE text, TASA_GAS decimal, VLP DECIMAL, IPR DECIMAL)''')
                if tabla=="EVENTO":
                    con.execute('''CREATE TABLE IF NOT EXISTS EVENTOS
                                (FECHA datetime, EVENTO text)''')
                if tabla == "WELLB":
                    con.execute('''CREATE TABLE IF NOT EXISTS WELLBORE
                                (NOMBRE text, TIPO text, DESCRIPCION text, ID DECIMAL, OD DECIMAL, MD DECIMAL, LONGITUD DECIMAL)''')
                mensaje = 'Datos actualizados'
                con.commit()
                # We can also close the connection if we are done with it.
                # Just be sure any changes have been committed or they will be lost.
                con.close()
                i += 1
            except Exception as e:
                print('ERROR: %s',e)
                mensaje = e
    return mensaje