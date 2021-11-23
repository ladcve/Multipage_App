import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Row import Row
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ALL, MATCH
from dash_html_components.Br import Br
import plotly.express as px
from plotly.subplots import make_subplots
import dash_table
import sqlite3
import configparser
import sys
import os.path
from os import listdir
from os.path import isfile, join
import pandas as pd
from datetime import date
from collections import OrderedDict
import base64
import json
import os
from io import StringIO
import contextlib

from app import app 

#https://www.youtube.com/watch?v=uSmOry4PY0Q&ab_channel=CharmingData

#Variable con la ruta para salvar los querys
QUERY_DIRECTORY = "./querys"

#Lee el archivo de configuracion
configuracion = configparser.ConfigParser()

#Variable con la ruta para salvar los querys
QUERY_DIRECTORY = "./querys"
CHART_DIRECTORY = "./template/"

# padding for the page content
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

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

#Listado de query
pathway = './querys'
files = [f for f in listdir(pathway) if isfile(join(pathway, f))]

file_name = ''
user_globals= {}

content = html.Div(id="container2", children=[], )
content2 = html.Div(id="results", children=[])

layout = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.Row([
                    dbc.Col([
                        html.Label(['Consulta:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                            id='dpd-query-data',
                            options=[
                                {'label': i, 'value': i} for i in files
                            ],
                            clearable=False
                        ),
                    ], width={"size": 4, "offset": 1}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button("Agregar Linea Comando", id="btn_add_command", color="success", className="mr-3"),
                    ]),
                ]),
                html.Br(),
            ]),
        ], width={"size": 6, "offset": 0}),
    ]),
    html.Br(),
    html.Div(content),
    
    # dcc.Store stores the intermediate value
    dcc.Store(id='intermediate-value'),
])

@contextlib.contextmanager
def stdoutIO(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old
    
def exec_function(user_input):
    try:
        compile(user_input, '<stdin>', 'eval')
    except SyntaxError:
        return exec
    return eval

def selected_user_globals(user_globals):
    return (
        (key, user_globals[key])
        for key in sorted(user_globals)
        if not key.startswith('__') or not key.startswith('__')
    )

def save_user_globals(user_globals, path='user_globals.txt'):
    with open(path, 'w') as fd:
        for key, val in selected_user_globals(user_globals):
            fd.write('%s = %s (%s)\n' % (
                key, val, val.__class__.__name__
            ))

@app.callback(
    Output("container2", "children"),
    [
        Input("btn_add_command", "n_clicks"),
        Input({"type": "dynamic-delete", "index": ALL}, "n_clicks"),
        Input("dpd-query-data", "value"),
    ],
    [State("container2", "children")],
)
def get_user_input(n_clicks, _, file_name, children):
    input_id = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
    if "index" in input_id:
        delete_chart = json.loads(input_id)["index"]
        children = [
            chart
            for chart in children
            if "'index': " + str(delete_chart) not in str(chart)
        ]
    if 'btn_add_command' in input_id:
      
        new_element = html.Div([
             dbc.Card([
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        dbc.Button("Ejecutar", id={"type": "dynamic-run", "index": n_clicks}, n_clicks=0, color="success", className="mr-3"),
                    ], width={"size": 1, "offset": 0}),
                    dbc.Col([
                        dbc.Input(id={"type": "dynamic-input", "index": n_clicks}, placeholder="Type something...", type="text", style={'backgroundColor':'white'}),
                        html.Div(id={"type": "dynamic-display-output", "index": n_clicks})
                    ], width={"size": 8, "offset": 0}),
                    dbc.Col([
                        html.Div(
                            dbc.Button("Borrar", id={"type": "dynamic-delete", "index": n_clicks}, n_clicks=0, color="warning", className="mr-3"),
                            className="d-grid gap-2 d-md-flex justify-content-md-end"
                        ),
                    ], width={"size": 1, "offset": 1}),
                ]),
                html.Br(),
            ])
        ])
        children.append(new_element)
    return children

@app.callback(
    Output({"type": "dynamic-display-output", "index": MATCH}, "children"),
    [
        Input({"type": "dynamic-input", "index": MATCH}, "value"),
        Input({"type": "dynamic-run", "index": MATCH}, "n_clicks"),
        Input('intermediate-value', 'data')
    ],
)
def display_output(user_input, n_clicks, data):
    message = ''
    if data is not None:
        df = pd.read_json(data, orient='split')
    context = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    if 'dynamic-run' in context and n_clicks > 0:
        if user_input is not None:
            save_user_globals(user_globals)
            try:
                with stdoutIO() as retval:
                    exec_function(user_input)(user_input, user_globals)
            except Exception as e:
                message = '%s: %s' % (e.__class__.__name__, e)
            else:
                if retval is not None:
                    message = 'Out: %s ' % (retval.getvalue())
    return message

@app.callback(Output('intermediate-value', 'data'),
    Input("dpd-query-data", "value")
)
def save_initial_data(file_name):
    con = sqlite3.connect(archivo)
    df = pd.DataFrame()
    if file_name:
        with open(os.path.join(QUERY_DIRECTORY, file_name)) as f:
            contenido = f.readlines()
            for linea in contenido:
                query =  linea +" ORDER BY FECHA"
            df =pd.read_sql(query, con)
        con.close()

    return df.to_json(date_format='iso', orient='split')
