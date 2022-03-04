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

#Variable con la ruta para salvar los querys
LOAD_DIRECTORY = "./datasets/"

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

layout = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Card([
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        html.Label(['Nombre de Archivo Excel:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dbc.Input(id="inp-ruta-excel", placeholder="Type something...", type="text", style={'backgroundColor':'white'}),
                        html.Div(id="loading-message")
                    ], width={"size": 3, "offset": 1}),
                    dbc.Col([
                        html.Br(),
                        dcc.Upload(
                            dbc.Button(html.Span(["archivo ", html.I(className="fas fa-upload ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                                id="btn_add_row", color="primary", n_clicks=0, className="mr-1"),
                            id='upload_excel_data',
                            # Allow multiple files to be uploaded
                            multiple=False
                        ),
                    ], width=2),
                    dbc.Col([
                        html.Label(['Pozo:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                            id='dpd-well-lists',
                            options=[{'label': i, 'value': i} for i in well_list],
                            clearable=False
                        ),
                    ], width=2),
                    dbc.Col([
                        html.Br(),
                        dbc.Button(html.Span(["salvar ", html.I(className="fas fa-save ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                         id="btn_save_excel_data", color="success", className="mr-3"),
                    ], width=2),
                ]),
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        html.Label(['Nombre de la hoja:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dbc.Input(id="inp_sheet_name", placeholder="Type something...", type="text", style={'backgroundColor':'white'}),
                        html.Div(id="save_message_excel")
                    ], width={"size": 2, "offset": 1}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button(html.Span(["ver ", html.I(className="fas fa-database ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                         id="btn_show_excel_data", color="primary", className="mr-3"),
                    ], width=2),
                ]),
                html.Br(),
            ]),
        ], width=7),
    ]),

    html.Br(),
    dbc.Row([
        dbc.Card([
            dbc.CardHeader(html.Label(['Datos Archivo Excel'],style={'font-weight': 'bold', "text-align": "left"})),
            dbc.CardBody([
                dcc.Loading(
                    dash_table.DataTable(id="query_results_excel", 
                    style_as_list_view=True,
                    editable=True,
                    row_deletable=True,
                    style_cell={'padding': '5px','fontSize':15, 'font-family':'arial'},
                    style_header={
                        'backgroundColor': 'blue',
                        'fontWeight': 'bold',
                        'color': 'white',
                        'font-family':'arial'
                    },
                    page_action="native",
                    page_current= 0,
                    page_size= 10,),
                ),
            ]),
        ], style={"background-color": "#F9FCFC"},),
    ]),
    dbc.Modal(
        [
            dbc.ModalHeader("Plantilla Salvada"),
        ],
        id="modal_survey",
        is_open=False,
    ),
])

@app.callback(Output('inp-ruta-excel', 'value'),
              [Input('upload_excel_data', 'filename'),
              Input('upload_excel_data', 'contents')]
              )
def update_output( list_of_names, list_of_contents):
    archivo = list_of_names
    contenido = list_of_contents
    if list_of_names is not None:
        archivo = list_of_names
    if list_of_contents is not None:
        contenido = list_of_contents
    return archivo

@app.callback(
    [Output("query_results_excel", "data"), Output("query_results_excel", "columns")],
    [Input("btn_show_excel_data", "n_clicks"),
     Input('inp-ruta-excel', 'value'), 
     Input('inp_sheet_name', 'value'),
     Input('dpd-well-lists', 'value')], 
    [State('query_results_excel', 'data'), State('query_results_excel', 'columns')]
)
def update_table_excel(n_clicks, excel_name, sheet_excel_name, well_name, data, columns):
    data_results = pd.DataFrame()
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

    if 'btn_show_excel_data' in changed_id:
        data_results = pd.read_excel(open(LOAD_DIRECTORY+excel_name, 'rb'), sheet_name=sheet_excel_name)  
        data_results['NOMBRE']=well_name

    columns = [{'name': i, 'id': i, 'renamable': True, 'deletable': True} for i in data_results.columns]
    data = data_results.to_dict('records')
    return data, columns

@app.callback(
    Output("modal_survey", "children"),
    Input("btn_save_excel_data", "n_clicks"),
    [State('query_results_excel', 'data'),State('modal_survey','is_open')]
)
def fupdate_table(n_clicks, dataset, is_open):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    mensaje = ''
    pg = pd.DataFrame(dataset)
    if 'btn_save_excel_data' in changed_id:
        con = sqlite3.connect(archivo)
        pg.to_sql('SURVEY', con, if_exists='append', index=False)
        con.commit()
        con.close()
        is_open=True
    return is_open