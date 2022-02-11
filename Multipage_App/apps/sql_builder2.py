import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Row import Row
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
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
import dash_ace
import os

from app import app 
from library import create_list, read_select, save_file

#Variable con la ruta para salvar los querys
QUERY_DIRECTORY = "./querys"

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

cursor = con.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables_list = pd.DataFrame (cursor.fetchall(), columns = ['name'])
#tables_list = tables_list.sort_values('name')['name'].unique()

layout = html.Div([
    dbc.Row([
        dbc.Col([
            dac.Box([
                dac.BoxHeader(
                    collapsible = False,
                    closable = False,
                    title="Elemento de la Consulta"
                ),
                dac.BoxBody([
                    dbc.Row([
                        dac.Box([
                                dac.BoxHeader(
                                    collapsible = False,
                                    closable = False,
                                    title="Tablas"
                                ),
                                dac.BoxBody([
                                    dash_table.DataTable(
                                        id="dt_tables", 
                                        columns = [dict(id='name', name='TABLAS', type='text')], 
                                        data = tables_list.to_dict('records'),
                                        filter_action="native",
                                        style_header={
                                            'backgroundColor': 'blue',
                                            'fontWeight': 'bold',
                                            'color': 'white',
                                            'font-family':'arial'
                                        },
                                        row_selectable="single",
                                        row_deletable=False,
                                        selected_columns=[],
                                        selected_rows=[0],
                                        page_current= 0,
                                        page_size= 8,
                                        #style_table={'height': '700px', 'overflowY': 'auto'},
                                        style_cell={'textAlign': 'left', 'minWidth': '100px', 'width': '200px', 'maxWidth': '300px', 'font-family':'arial'},
                                    ),
                                ]),	
                            ],
                            color='primary',
                            solid_header=True,
                            elevation=4,
                            width=12
                        ),
                    ]),
                    dbc.Row([
                        dac.Box([
                                dac.BoxHeader(
                                    collapsible = False,
                                    closable = False,
                                    title="Atributos"
                                ),
                                dac.BoxBody([
                                    dash_table.DataTable(id="td_tables_fields", 
                                    style_as_list_view=True,
                                    style_header={
                                        'backgroundColor': 'blue',
                                        'fontWeight': 'bold',
                                        'color': 'white'
                                    },
                                    row_selectable="multi",
                                    row_deletable=False,
                                    selected_columns=[],
                                    selected_rows=[],
                                    page_action="native",
                                    page_current= 0,
                                    style_cell={'textAlign': 'left', 'minWidth': '100px', 'width': '200px', 'maxWidth': '300px', 'font-family':'arial'},
                                    page_size= 8,),
                                ]),	
                            ],
                            color='primary',
                            solid_header=True,
                            elevation=4,
                            width=12
                        ),
                    ]),
                ]),
            ],
            color='primary',
            solid_header=True,
            elevation=4,
            width=12
            ),
        ], width={"size": 3, "offset": 0}),
        dbc.Col([
            dbc.Card([
                dbc.Row([
                    dbc.Col([
                        dbc.Row(dbc.Col(html.Label(['Nombre de Archivo:'],style={'font-weight': 'bold', "text-align": "left"}),)),
                        dbc.Input(id="inp-query-edit", placeholder="Type something...", type="text", style={'backgroundColor':'white'}),
                        html.Div(id="loading-file-message")
                    ], width={"size": 4, "offset": 1}),
                    dbc.Col([
                        html.Br(),
                        dcc.Upload(
                            dbc.Button(html.Span(["cargar ", html.I(className="fas fa-upload ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                            id="btn-upload-sql", color="primary", n_clicks=0, className="mr-1"),
                            # Allow multiple files to be uploaded
                            id='upload_sql_file',
                            multiple=False
                        ),
                    ], width={"size": 1, "offset": 0}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button(html.Span(["salvar ", html.I(className="fas fa-save ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                        id="btn_save_query", color="primary", n_clicks=0, className="mr-1"),
                        html.Div(id="save_message_query"),
                    ], width={"size": 1, "offset": 1}),
                ]),
                html.Br(),
            ]),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dac.Box([
                        dac.BoxHeader(
                            collapsible = False,
                            closable = False,
                            title="Consulta"
                        ),
                        dac.BoxBody([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button(html.Span(["crear ", html.I(className="fa fa-random")],style={'font-size':'1.5em','text-align':'center'}),
                                    id="btn_create_query", color="success", n_clicks=0, className="mr-1"),
                                    dcc.ConfirmDialog(
                                        id='confirm-error',
                                        message='Hay un error en la sentencia SQL.',
                                    ),
                                ], width={"size": 1, "offset": 1}),
                                dbc.Col([
                                    dbc.Button(html.Span(["ejecutar ", html.I(className="fa fa-play-circle")],style={'font-size':'1.5em','text-align':'center'}),
                                    id="btn_run_query", color="success", n_clicks=0, className="mr-1"),
                                ], width={"size": 1, "offset": 1}),
                            ]),
                            html.Br(),
                            dbc.Row([
                                dash_ace.DashAceEditor(
                                    id='textarea-edit',
                                    value='',
                                    theme='github',
                                    mode='sql',
                                    setOptions=({
                                        'maxline' : 100,
                                    }),
                                    tabSize=4,
                                    height='350px',
                                    width ='900px',
                                    enableBasicAutocompletion=True,
                                    enableLiveAutocompletion=True,
                                    autocompleter='/autocompleter?prefix=',
                                    placeholder='código SQL'
                                ),
                            ]),
                        ]),	
                    ],
                    color='primary',
                    solid_header=True,
                    elevation=4,
                    width=12
                    ),
                ], width={"size": 8, "offset": 0}),
                dbc.Col([
                    dac.Box([
                        dac.BoxHeader(
                            collapsible = False,
                            closable = False,
                            title="Filtrado"
                        ),
                        dac.BoxBody([
                            html.Label(['Campos:'],style={'font-weight': 'bold', "text-align": "left"}),
                            dcc.Dropdown(
                                id='dpd-fields',
                                clearable=False
                            ),
                            html.Label(['Operadores:'],style={'font-weight': 'bold', "text-align": "left"}),
                            dcc.Dropdown(id='dpd-operator',
                                options=[
                                    {'label': '=', 'value': '='},
                                    {'label': '!=', 'value': '!='},
                                    {'label': '<>', 'value': '<>'},
                                    {'label': '<', 'value': '<'},
                                    {'label': '>', 'value': '>'},
                                    {'label': '<=', 'value': '<'},
                                    {'label': '>=', 'value': '>'},
                                ],
                                value='='
                            ),
                            html.Label(['Valor:'],style={'font-weight': 'bold', "text-align": "left"}),
                            dbc.Input(id="inp-value-cond", placeholder="Type something...", type="text", style={'backgroundColor':'white'}),
                            html.Br(),
                            dbc.Button(html.Span(["adicionar ", html.I(className="fa-solid fa-circle-plus")],style={'font-size':'1.5em','text-align':'center'}),
                            id="btn_add", color="success", n_clicks=0, className="mr-1"),
                        ]),	
                    ],
                    color='primary',
                    solid_header=True,
                    elevation=4,
                    width=12
                    ),
                    dac.Box([
                        dac.BoxHeader(
                            collapsible = False,
                            closable = False,
                            title="condiciones"
                        ),
                        dac.BoxBody([
                            dash_ace.DashAceEditor(
                                id='textarea-condition',
                                value='',
                                theme='github',
                                mode='sql',
                                setOptions=({
                                    'maxline' : 100,
                                }),
                                tabSize=4,
                                height='100px',
                                width ='470px',
                                enableBasicAutocompletion=True,
                                enableLiveAutocompletion=True,
                                autocompleter='/autocompleter?prefix=',
                                placeholder='código SQL'
                            )
                        ]),	
                    ],
                    color='primary',
                    solid_header=True,
                    elevation=4,
                    width=12
                    ),
                ], width={"size": 4, "offset": 0}),
            ]),
            dbc.Row([
                dac.Box([
                        dac.BoxHeader(
                            collapsible = False,
                            closable = False,
                            title="Resultados"
                        ),
                        dac.BoxBody([
                            dbc.Spinner(
                                dash_table.DataTable(id="dt_query_results", 
                                style_as_list_view=True,
                                style_cell={'padding': '5px'},
                                style_header={
                                    'backgroundColor': 'blue',
                                    'fontWeight': 'bold',
                                    'color': 'white'
                                },
                                page_action="native",
                                page_current= 0,
                                page_size= 7,),
                            ),
                        ]),	
                    ],
                    color='primary',
                    solid_header=True,
                    elevation=4,
                    width=12
                ),
            ]),
        ], width={"size": 9, "offset": 0}),
    ]),
])

@app.callback(
    [Output("td_tables_fields", "data"), Output("td_tables_fields", "columns")],
    [Input('dt_tables', 'data'),
    Input('dt_tables', 'derived_virtual_selected_rows')], 
    [State('td_tables_fields', 'data'), State('td_tables_fields', 'columns')]
)
def update_table_results(rows, row_id, data, columns):
    df_fields = pd.DataFrame()
    if row_id:
        indice = row_id[0]
        table_name = rows[indice]['name']

        con = sqlite3.connect(archivo)
        query = "PRAGMA table_info('"+table_name+"')"
        df = pd.read_sql(query, con)
        df_fields['CAMPOS'] = df['name']
        con.close()

    columns = [{'name': i, 'id': i} for i in df_fields.columns]
    data = df_fields.to_dict('records')

    return data, columns


@app.callback(
    [Output("textarea-edit", "value"),
     Output('inp-query-edit', 'value'),
     ],
    [Input('btn_create_query', 'n_clicks'),
     Input('dt_tables', 'data'),
    Input('dt_tables', 'derived_virtual_selected_rows'),
    Input('td_tables_fields', 'data'),
    Input('td_tables_fields', 'derived_virtual_selected_rows'),
    Input('upload_sql_file', 'filename'),
    Input('upload_sql_file', 'contents'),
    Input('textarea-condition','value')], 
)
def create_query(n_clicks, tables_rows, tables_rowid, fields_rows, fields_rowids, list_of_names, list_of_contents, condition):
    field_list = []
    archivo = ''
    new_query = ''

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'btn_create_query' in changed_id:
        new_query = ''
        indice = tables_rowid[0]
        table_name = tables_rows[indice]['name']

        for num_id in fields_rowids:
            field_list.append(fields_rows[num_id]['CAMPOS'])
        
        new_query = read_select(table_name, field_list, [])

        for linea in condition.splitlines():
            if new_query.find("WHERE")>1:
                new_query += " AND "+linea
            else:
                new_query += " WHERE "+linea
    else:
        if list_of_names and list_of_contents:
            new_query = ''
            archivo = list_of_names
            if archivo:
                with open(os.path.join(QUERY_DIRECTORY, archivo)) as f:
                    contenido = f.readlines()
                    if contenido:
                        for linea in contenido:
                            new_query +=  linea 

    return new_query, archivo

@app.callback(
    [Output("dt_query_results", "data"), Output("dt_query_results", "columns"),
     Output('confirm-error', 'displayed')],
    [Input('btn_run_query', 'n_clicks'),
    Input("textarea-edit", "value"),
    ]
)
def execute_query(n_clicks, query):
    data_results =pd.DataFrame()
    display_message = False

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'btn_run_query' in changed_id:
        if query:
            try:
                con = sqlite3.connect(archivo)
                data_results = pd.read_sql(query, con)
            except:
                 display_message = True

    columns = [{'name': i, 'id': i} for i in data_results.columns]
    data = data_results.to_dict('records')

    return data, columns,  display_message


@app.callback(
    Output('save_message_query', 'children'),
    [Input('btn_save_query', 'n_clicks'),
     Input('textarea-edit', 'value'),
     Input('inp-query-edit', 'value')],
)
def save_query_file(n_clicks, textarea_query, file_name):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    mensaje = ''
    if 'btn_save_query' in changed_id:
         if file_name  and textarea_query: 
            save_file(file_name, textarea_query)
            mensaje='Salvado'
    return mensaje

 
@app.callback(
    Output('dpd-fields','options'),
    [Input('td_tables_fields', 'data'),
    Input('td_tables_fields', 'derived_virtual_selected_rows')],
)
def dropdown_fill(fields_data, fields_rowid):
    field_list=[]
    options = [{'label': i, 'value': i} for i in []]
    if fields_rowid:
        for num_id in fields_rowid:
            field_list.append(fields_data[num_id]['CAMPOS'])
        options = [{'label': i, 'value': i} for i in field_list]
    return options

@app.callback(
    Output('textarea-condition','value'),
    [Input('btn_add', 'n_clicks'),
    Input('dpd-fields', 'value'),
    Input('dpd-operator', 'value'),
    Input('inp-value-cond', 'value'),
    Input('textarea-condition','value'),],
)
def dropdown_fill(n_clicks, field, operator, val_cond, condition):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'btn_add' in changed_id:
        if field and operator and val_cond:
            condition += field+operator+val_cond+chr(10)
    return condition