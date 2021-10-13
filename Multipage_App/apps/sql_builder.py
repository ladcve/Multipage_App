import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Row import Row
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash_html_components.Br import Br
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
tables_list = tables_list.sort_values('name')['name'].unique()

#Seccion de funciones
def prefijo_tabla(tabla):
    prefijo =''
    if tabla=='CIERRE_DIARIO_POZO':
        prefijo='CEP'
    if tabla=='LECTURAS_POZO':
        prefijo='LEP'
    if tabla=='ESTIMACIONES_POZO':
        prefijo='ESP'
    if tabla=='PERDIDAS_POZO':
        prefijo='PEP'
    if tabla=='POTENCIAL_POZO':
        prefijo='POP'
    if tabla=='PRUEBAS_POZO':
        prefijo='PUP'
    return prefijo

#Salvar archivo
def save_file(name, content):
    """Decode and store a file uploaded with Plotly Dash."""
    data = content.encode("utf8").split(b";base64,")[0]
    with open(os.path.join(QUERY_DIRECTORY, name), "w") as fp:
       # fp.write(base64.decodebytes(data))
       fp.write(content)


layout = html.Div([
    dbc.Row(dbc.Col(html.Label(['Nombre de Archivo:'],style={'font-weight': 'bold', "text-align": "left"}),)),
    dbc.Row([
        dbc.Col([
            dbc.Input(id="input-ruta", placeholder="Type something...", type="text", style={'backgroundColor':'white'}),
            html.Div(id="loading-message")
        ], width=4),
        dbc.Col([
            dcc.Upload(
                html.Button('Cargar Archivo'),
                id='upload-data',
                # Allow multiple files to be uploaded
                multiple=False
            ),
        ], width=2),
         dbc.Col([
             dbc.Button("Savar Archivo", id="btn_save_file", color="primary", n_clicks=0, className="mr-1"),
             dcc.Download(id="save_file")
        ], width=1),
    ]),
    html.Br(),
     dbc.Row([
        dbc.Col([
            dbc.Card([
                    dbc.CardBody([
                         dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardHeader(html.Label(['SELECT'],style={'font-weight': 'bold', "text-align": "left"})),
                                    dbc.CardBody(
                                        dcc.Textarea(
                                            id='textarea-fields',
                                            value='SELECT ',
                                            style={'width': '100%', 'height': 110, 'background-color' : '#d1d1d1'},
                                        ),
                                    ),
                                ], color="light", ),
                                dbc.Card([
                                    dbc.CardHeader(html.Label(['FROM'],style={'font-weight': 'bold', "text-align": "left"})),
                                    dbc.CardBody(
                                        dcc.Textarea(
                                            id='textarea-tables',
                                            value='FROM ',
                                            style={'width': '100%', 'height': 110, 'background-color' : '#d1d1d1'},
                                        ),
                                    ),
                                ], color="light", ),
                                html.Br(),

                                dbc.Row([
                                    dbc.Button("Ejecutar", id="ejecutar_query", color="success", n_clicks=0, className="mr-2"),
                                    dbc.Col(html.Label(['F5 para limpiar la pantalla'],style={'font-weight': 'bold', "text-align": "left"})),
                                ]),
                            ]),
                            dbc.Col([
                                dbc.Card([
                                        dbc.CardHeader(html.Label(['WHERE'],style={'font-weight': 'bold', "text-align": "left"})),
                                        dbc.CardBody(
                                            dcc.Textarea(
                                                id='textarea-where',
                                                value='',
                                                style={'width': '100%', 'height': 300, 'background-color' : '#d1d1d1'},
                                            ),
                                        ),
                                ], color="light", ),
                                html.Br(),
                                
                                
                            ]),
                         ]),
                    ]),
            ], color="light", ),
        ], width=8),
        dbc.Col([
            dbc.Card([
                    dbc.CardHeader(html.Label(['Parametros'],style={'font-weight': 'bold', "text-align": "left"})),
                    dbc.CardBody([
                        html.Label(['Tablas'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                                id='list-tables',
                                options=[{'label': i, 'value': i} for i in tables_list],
                                clearable=False
                            ),
                        html.Br(),
                        html.Label(['Atributos'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                                id='list-atributes',
                                clearable=False,
                                multi=True
                            ),

                        html.Br(),
                        dbc.Button("Agregar Elementos", id="add_elements", color="success", className="mr-1"),
                        html.Br(),
                        html.Br(),
                        html.Label(['Condiciones:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dbc.Input(id="input-condition", placeholder="Type something...", type="text", style={'backgroundColor':'white'}),
                        html.Br(),
                        html.Label(['Ordenado por'],style={'font-weight': 'bold', "text-align": "left"}),
                        dbc.Input(id="input-order", placeholder="Type something...", type="text", style={'backgroundColor':'white'}),
                        html.Br(),
                        html.Label(['Agrupado por'],style={'font-weight': 'bold', "text-align": "left"}),
                        dbc.Input(id="input-group", placeholder="Type something...", type="text", style={'backgroundColor':'white'}),
                        
                    ]),
            ], color="light", ),
        ], width=4),
     ]),
    html.Br(),
    dbc.Row([
        dbc.Card([
            dbc.CardHeader(html.Label(['Resultados Consulta'],style={'font-weight': 'bold', "text-align": "left"})),
            dbc.CardBody([
                dbc.Spinner(
                    dash_table.DataTable(id="query_results", 
                    style_as_list_view=True,
                    style_cell={'padding': '5px'},
                    style_header={
                        'backgroundColor': 'blue',
                        'fontWeight': 'bold',
                        'color': 'white'
                    },
                    page_action="native",
                    page_current= 0,
                    page_size= 10,),
                ),
            ]),
        ]),
    ]),
])

@app.callback(
    Output('list-atributes', 'options'),
    [Input('list-tables', 'value')])
def set_atributes_options(table_selected):
    con = sqlite3.connect(archivo)
    table_selected = str(table_selected)
    cursor = con.execute("SELECT name FROM pragma_table_info('"+table_selected+"') WHERE name <> 'index' ")
    columns_names = pd.DataFrame (cursor.fetchall(), columns = ['name'])
    columns_names =  columns_names[columns_names!= np.array(None)]
    columns_names = columns_names.sort_values('name')['name'].unique()
    return [{"label": x, "value": x} for x in columns_names]

@app.callback(
    [Output('textarea-fields', 'value'),
    Output('textarea-tables', 'value'),
    Output('textarea-where', 'value')],
    [Input("add_elements", "n_clicks"), Input('list-atributes', 'value'),
    Input('list-tables', 'value'), 
    Input('textarea-fields', 'value'), 
    Input('textarea-tables', 'value'),
    Input('textarea-where', 'value')])
def selected_tables(n_clicks,atributes_selected, table_selected, textarea_fields, textarea_tables, textarea_where):
    atributes_list = textarea_fields
    tables_list = textarea_tables
    where_condition = textarea_where
    prefijo_ant = ''
    prefijo = prefijo_tabla(table_selected)

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'add_elements' in changed_id:
        for atribute in atributes_selected:
            if atributes_list == 'SELECT ':
                atributes_list = atributes_list  + prefijo + '.'+ atribute 
            else:
                atributes_list = atributes_list + ',' + prefijo + '.'+ atribute 
        if tables_list == 'FROM ':
            tables_list = tables_list  + table_selected + ' AS ' + prefijo 
        else:
            prefijo_ant = tables_list[-3:]
            tables_list = tables_list  + ',' + table_selected + ' AS ' + prefijo 
            where_condition = where_condition + 'WHERE '+prefijo_ant+'.NOMBRE='+prefijo+'.NOMBRE AND ' +prefijo_ant+'.FECHA='+prefijo+'.FECHA'         
    return atributes_list, tables_list, where_condition


@app.callback(
    [Output("query_results", "data"), Output("query_results", "columns")],
    [Input("ejecutar_query", "n_clicks"),
     Input('textarea-fields', 'value'), 
     Input('textarea-tables', 'value'),
     Input('textarea-where', 'value')],
    [State('query_results', 'data'), State('query_results', 'columns')]
)
def update_table(n_clicks, textarea_fields, textarea_tables, textarea_where, data, columns):
    data_results = pd.DataFrame()
    quer= ''
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

    if 'ejecutar_query' in changed_id:
        con = sqlite3.connect(archivo)
        query =  textarea_fields+' '+ textarea_tables+' '+ textarea_where
        data_results =pd.read_sql(query, con)
        n_clicks=0

    columns = [{'name': i, 'id': i} for i in data_results.columns]
    data = data_results.to_dict('records')
    return data, columns

@app.callback(Output('input-ruta', 'value'),
              [Input('upload-data', 'filename'),
              Input('upload-data', 'contents')]
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
    Output("loading-message", "children"),
    [Input("btn_save_file", "n_clicks"),
     Input('textarea-fields', 'value'), 
     Input('textarea-tables', 'value'),
     Input('textarea-where', 'value'),
     Input('input-ruta', 'value')],
)
def func(n_clicks, textarea_fields, textarea_tables, textarea_where, file_name):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    query =  textarea_fields+' '+ textarea_tables+' '+ textarea_where
    mensaje = ''
    if 'btn_save_file' in changed_id:
         if file_name is not None and query is not None: 
            save_file(file_name, query)
            mensaje='Archivo Salvado'
    return mensaje