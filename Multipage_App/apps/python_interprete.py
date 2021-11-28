import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Row import Row
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ALL, MATCH
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
import dash_ace

from app import app 

#https://www.youtube.com/watch?v=uSmOry4PY0Q&ab_channel=CharmingData

#Definir imagenes
open_chart = '.\pictures\open_chart.png'
open_chart_base64 = base64.b64encode(open(open_chart, 'rb').read()).decode('ascii')

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
                        html.Label(['Tabla:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dbc.Input(id='inp-table-name', placeholder="Type something...", type="text", style={'backgroundColor':'white'}),
                    ], width={"size": 4, "offset": 1}),
                    dbc.Col([
                         html.Br(),
                        dbc.Button("Salva a BD", id="btn_save_db", color="primary", n_clicks=0, className="mr-1"),
                    ], width={"size": 1, "offset": 0}),
                ]),
                html.Br(),
            ]),
        ], width={"size": 10, "offset": 0}),
    ]),
    html.Br(),
    html.Div(id='dummy1'),
    dbc.Row([
        dbc.Col([
            dbc.Button("Ejecutar", id="btn_run", color="success", n_clicks=0, className="mr-1"),
            html.Br(),
            dbc.Card([
                dbc.CardHeader(html.Label(['Codigo'],style={'font-weight': 'bold', "text-align": "left"})),
                dbc.CardBody(
                    dash_ace.DashAceEditor(
                        id='textarea-code',
                        value='import pandas as pd\n'
                            'df = pd.read_csv("./datasets/read_data.csv")',
                        theme='github',
                        mode='python',
                        setOptions=({
                            'maxline' : 100,
                        }),
                        tabSize=1,
                        enableBasicAutocompletion=True,
                        enableLiveAutocompletion=True,
                        autocompleter='/autocompleter?prefix=',
                        placeholder='Python code ...'
                    )
                ),
            ]),
        ]),
        dbc.Col([
            html.Br(),
            dbc.Card([
                dbc.CardHeader(html.Label(['Shell'],style={'font-weight': 'bold', "text-align": "left"})),
                dbc.CardBody(
                    dcc.Textarea(
                        id='textarea-shell',
                        value='',
                        style={'width': '100%', 'height': 1000, 'background-color' : '#d1d1d1'},
                    ),
                ),
            ]),
        ])
    ])
    
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

@app.callback(Output("dummy1", "children"),
    Input("dpd-query-data", "value")
)
def save_initial_data(file_name):
    con = sqlite3.connect(archivo)
    df = pd.DataFrame()
    if file_name:
        with open(os.path.join(QUERY_DIRECTORY, file_name)) as f:
            contenido = f.readlines()
            for linea in contenido:
                query =  linea
            df =pd.read_sql(query, con)
        con.close()
        df.to_csv("./datasets/read_data.csv")
    return None

@app.callback(
    Output("textarea-shell", "value"),
    [
        Input("textarea-code", "value"),
        Input("btn_run", "n_clicks"),
    ],
)
def display_output(user_input, n_clicks):
    results = ''
    input_list = user_input.splitlines()
    context = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    if 'btn_run' in context and n_clicks > 0:
        if user_input is not None:
            for linea in input_list:
                save_user_globals(user_globals)
                try:
                    with stdoutIO() as retval:
                        exec_function(linea)(linea, user_globals)
                except Exception as e:
                    results = '%s: %s' % (e.__class__.__name__, e)
                else:
                    if retval is not None:
                        results = 'Out: %s ' % (retval.getvalue())
    return results