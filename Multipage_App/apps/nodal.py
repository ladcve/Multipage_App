import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Row import Row
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import dash_admin_components as dac
import plotly.express as px
from plotly.subplots import make_subplots
import dash_table
import sqlite3
import configparser
import sys
import os.path
import os
from os import listdir
from os.path import isfile, join
import numpy as np
import pandas as pd
from datetime import date
from collections import OrderedDict
import base64
import json
import os
import dash_daq as daq

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
                        dbc.Input(id="inp-ruta-excel-nodal", placeholder="Type something...", type="text", style={'backgroundColor':'white'}),
                        html.Div(id="loading-message")
                    ], width={"size": 3, "offset": 1}),
                    dbc.Col([
                        html.Br(),
                        dcc.Upload(
                            dbc.Button(html.Span(["CARGAR ", html.I(className="fas fa-upload ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                        id="upload_excel_data_nodal", color="success", className="mr-3"),
                            # Allow multiple files to be uploaded
                            multiple=False
                        ),
                    ], width={"size": 2, "offset": 1}),
                    dbc.Col([
                        html.Label(['Pozo:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                            id='dpd-well-lists-nodal',
                            options=[{'label': i, 'value': i} for i in well_list],
                            clearable=False
                        ),
                    ], width={"size": 1, "offset": 0}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button(html.Span(["Grabar ", html.I(className="fas fa-save ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                        id="btn_save_excel_data_nodal", color="success", className="mr-3"),
                    ], width={"size": 1, "offset": 0}),
                ]),
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        html.Label(['Nombre de la hoja:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dbc.Input(id="inp_sheet_name_nodal", placeholder="Type something...", type="text", style={'backgroundColor':'white'}),
                        html.Div(id="save_message_excel")
                    ], width={"size": 2, "offset": 1}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button(html.Span(["VER ", html.I(className="fas fa-database ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                         id="btn_show_excel_data_nodal", color="primary", className="mr-3"),
                    ], width={"size": 1, "offset": 0}),
                ]),
                html.Br(),
            ]),
        ], width={"size": 7, "offset": 0}),
    ]),

    html.Br(),
    dbc.Row([
        dac.Box([
                dac.BoxHeader(
                    collapsible = False,
                    closable = False,
                    title="Datos Archivo Excel"
                ),
                dac.BoxBody([
                    dbc.Spinner(
                        dash_table.DataTable(id="query_results_excel_nodal", 
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
            ],
            color='primary',
            solid_header=True,
            elevation=4,
            width=12
        ),
        dbc.Card([
            dbc.CardHeader(html.Label([''],style={'font-weight': 'bold', "text-align": "left"})),
            dbc.CardBody([

            ]),
        ]),
        dac.Box([
                dac.BoxHeader(
                    collapsible = False,
                    closable = False,
                    title="Datos Archivo Excel"
                ),
                dac.BoxBody([
                    dbc.Spinner(
                        dcc.Graph(id='cht-nodal-chart'),
                    ),
                ]),	
            ],
            color='primary',
            solid_header=True,
            elevation=4,
            width=12
        ),
    ])
])

@app.callback(Output('inp-ruta-excel-nodal', 'value'),
              [Input('upload_excel_data_nodal', 'filename'),
              Input('upload_excel_data_nodal', 'contents')]
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
    Output('cht-nodal-chart','figure'),
    [Input("query_results_excel_nodal", "data"),
    Input("btn_show_excel_data_nodal", "value"),
    ]
)
def update_nodal_chart(rows, well_name):
    df = pd.DataFrame(rows)
    numbers = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]
    fig = {}
    if (len(df.columns)>1 and well_name):
        df= df.loc[df['NOMBRE']==well_name]
        se = pd.Series(numbers)
        df['Point'] = se.values
        fig = px.line(df, x='Point', y=['VLP', 'IPR'])
        fig.update_xaxes(showline=True, linewidth=2, linecolor='black', showgrid=False,)
        fig.update_yaxes(showline=True, linewidth=2, linecolor='black', showgrid=False,)
        fig.update_layout(
                    autosize=False,
                    width=800,
                    height=780,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgb(240, 240, 240)',
                   )

    return fig

@app.callback(
    [Output("query_results_excel_nodal", "data"), Output("query_results_excel_nodal", "columns")],
    [Input("btn_show_excel_data_nodal", "n_clicks"),
     Input('inp-ruta-excel-nodal', 'value'), 
     Input('inp_sheet_name_nodal', 'value'),
     Input('dpd-well-lists-nodal', 'value')], 
    [State('query_results_excel_nodal', 'data'), State('query_results_excel_nodal', 'columns')]
)
def update_table_excel_nodal(n_clicks, excel_name, sheet_excel_name, well_name, data, columns):
    data_results = pd.DataFrame()
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

    if 'btn_show_excel_data' in changed_id:
        data_results = pd.read_excel(open(LOAD_DIRECTORY+excel_name, 'rb'), sheet_name=sheet_excel_name)  
        data_results['NOMBRE']=well_name

    columns = [{'name': i, 'id': i, 'renamable': True, 'deletable': True} for i in data_results.columns]
    data = data_results.to_dict('records')
    return data, columns

@app.callback(
    Output("save_message_excel_nodal", "children"),
    Input("btn_save_excel_data_nodal", "n_clicks"),
    [State('query_results_excel_nodal', 'data')]
)
def update_table_nodal(n_clicks, dataset):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    mensaje = ''
    pg = pd.DataFrame(dataset)
    if 'btn_save_excel_data' in changed_id:
        con = sqlite3.connect(archivo)
        pg.to_sql('NODAL', con, if_exists='append', index=False)
        con.commit()
        con.close()
        mensaje='Datos guardados'
    return mensaje

