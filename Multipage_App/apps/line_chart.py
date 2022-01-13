import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Row import Row
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash_table.Format import Format, Symbol
import dash_admin_components as dac
import plotly.graph_objects as go
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

#Definir imagenes
open_chart = '.\pictures\open_chart.png'
open_chart_base64 = base64.b64encode(open(open_chart, 'rb').read()).decode('ascii')

#Lee el archivo de configuracion
configuracion = configparser.ConfigParser()

#Variable con la ruta para salvar los querys
QUERY_DIRECTORY = "./querys"
CHART_DIRECTORY = "./template/"

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

query = "SELECT NOMBRE FROM VARIABLES"
var_list =pd.read_sql(query, con)
var_list = var_list.sort_values('NOMBRE')['NOMBRE'].unique()

#Listado de eventos
query = "SELECT * FROM EVENTOS"
event_list =pd.read_sql(query, con)

#Listado de unidades por variables
query = "SELECT * FROM UNIDADES"
unidades =pd.read_sql(query, con)

con.close()

#Listado de query
pathway = './querys'
files = [f for f in listdir(pathway) if isfile(join(pathway, f))]

file_name = ''
tab_height = '2vh'

layout = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.Row([
                    dbc.Col([
                        html.Label(['Consulta:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                            id='dpd-consulta-lista',
                            options=[
                                {'label': i, 'value': i} for i in files
                            ],
                            clearable=False
                        ),
                    ], width={"size": 4, "offset": 1}),
                    dbc.Col([
                        html.Label(['Pozo:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                            id='dpd-pozo-lista',
                            options=[{'label': i, 'value': i} for i in well_list],
                            clearable=False,
                            multi=True
                        ),
                    ], width={"size": 4, "offset": 0}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button(
                            html.Span(["Mostrar ", html.I(className="fas fa-chart-bar ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                            id="btn_show_chart",
                            color="success",
                            className="me-1"
                        )
                    ]),
                ]),
                html.Br(),
            ]),
        ], width={"size": 6, "offset": 0}),
        dbc.Col([
            dbc.Card([
                dbc.Row([
                    dbc.Col([
                        html.Label(['Nombre Plantilla:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dbc.Input(id="inp-ruta-linechart", placeholder="Type something...", type="text", style={'backgroundColor':'white'}),
                    ], width={"size": 3, "offset": 1}),
                     dbc.Col([
                        html.Br(),
                        dcc.Upload(
                            dbc.Button(
                                html.Span(["Abrir ", html.I(className="fas fa-upload ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                                n_clicks=0, color="primary", className="mr-3"
                            ),
                            id='btn_open_linechart',
                            multiple=False
                        ),
                    ], width={"size": 3, "offset": 0}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button(html.Span(["Grabar ", html.I(className="fas fa-save ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                            id="btn_save_linechart", 
                            n_clicks=0, 
                            color="primary", 
                            className="mr-3"
                        ),
                        html.Div(id="save_message_linechart"),
                    ]),
                ]),
                html.Br(),
            ]),
        ], width={"size": 6, "offset": 0}),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dac.Box([
                dac.BoxHeader(
                    collapsible = False,
                    closable = False,
                    title="Gráfico de Líneas"
                ),
                dac.BoxBody(
                    dbc.Spinner(
                        dcc.Graph(id='cht-line-chart', style={"width": "100%" }),
                    ),
                ),	
                ],
                color='primary',
                solid_header=True,
                elevation=4,
                width=12
            ),
        ], width={"size": 9,"offset": 0}),
        dbc.Col([
            dac.Box([
                dac.BoxHeader(
                    collapsible = False,
                    closable = False,
                    title="Parametros"
                ),
                dac.BoxBody([
                    dcc.Tabs(style={
                        'width': '50%',
                        'font-size': '100%',
                        'height':tab_height
                    },children=[
                        dcc.Tab(label='Opciones', style={'padding': '0','line-height': tab_height},selected_style={'padding': '0','line-height': tab_height}, children=[
                            html.Br(),
                            dcc.Checklist(
                                id="cb_clear_data_line",
                                options=[{"label": "  Limpiar valores Ceros", "value": "YES"}],
                                value=[],
                                labelStyle={"display": "inline-block"},
                            ),
                            html.Br(),
                            dbc.Card([
                                dbc.CardHeader(html.Label(['Eje Primario'],style={'font-weight': 'bold', "text-align": "left"})),
                                dbc.CardBody([
                                    html.Label(['Datos:'],style={'font-weight': 'bold', "text-align": "left"}),
                                    dcc.Dropdown(
                                        id='dpd-column-list-y1',
                                        clearable=False,
                                        multi=True
                                    ),
                                    html.Label(['color:'],style={'font-weight': 'bold', "text-align": "left"}),
                                    dbc.Input(
                                        type="color",
                                        id="inp-color-list-y1",
                                        value="#1530E3",
                                        style={"width": 75, "height": 50},
                                    ),
                                ]),
                            ]),
                            dbc.Card([
                                dbc.CardHeader(html.Label(['Eje Secundario'],style={'font-weight': 'bold', "text-align": "left"})),
                                dbc.CardBody([
                                    html.Label(['Datos:'],style={'font-weight': 'bold', "text-align": "left"}),
                                    dcc.Dropdown(
                                        id='dpd-column-list-y2',
                                        clearable=False,
                                        multi=True
                                    ),
                                    html.Label(['color:'],style={'font-weight': 'bold', "text-align": "left"}),
                                    dbc.Input(
                                        type="color",
                                        id="inp-color-list-y2",
                                        value="#1530E3",
                                        style={"width": 75, "height": 50},
                                    ),
                                ]),
                            ]),
                            dbc.Card([
                                dbc.CardBody([
                                    html.Label(['Variable Calculadas:'],style={'font-weight': 'bold', "text-align": "left"}),
                                    dcc.Dropdown(
                                        id='dpd-var-list-chart',
                                        options=[{'label': i, 'value': i} for i in var_list],
                                        clearable=False,
                                        multi=True,
                                    ),
                                ])
                            ]),
                        ]),
                        dcc.Tab(label='Eventos', style={'padding': '0','line-height': tab_height},selected_style={'padding': '0','line-height': tab_height},children=[
                            dbc.Card([
                                dbc.CardHeader(html.Label(['Eventos'],style={'font-weight': 'bold', "text-align": "left"})),
                                dbc.CardBody([
                                    daq.ToggleSwitch(
                                        id='ts-annotation',
                                        value=False,
                                        label='Mostrar Anotaciones',
                                        labelPosition='top'
                                    ),
                                    dash_table.DataTable(id="dt_table_event", 
                                        columns = [{'name': i, 'id': i, "deletable": True} for i in event_list.columns],
                                        data = event_list.to_dict('records'),
                                        style_as_list_view=True,
                                        style_cell={'padding': '5px', 'textAlign':'left','fontSize':10, 'font-family':'arial'},
                                        style_table={
                                            'overflowX': 'auto',
                                            'whiteSpace': 'normal',
                                            'height': 'auto',
                                        },
                                        style_header={
                                            'backgroundColor': 'blue',
                                            'fontWeight': 'bold',
                                            'color': 'white',
                                            'textAlign':'center',
                                            'fontSize':10,
                                            'font-family':'arial'
                                        },),
                                ]),
                            ]),
                        ]),
                    ]),
                ]),	
                ],
                color='primary',
                solid_header=True,
                elevation=4,
                width=12
            ),
        ], width=3),
    ]),
])

@app.callback(
    Output('cht-line-chart','figure'),
    [Input("btn_show_chart", "n_clicks"),
     Input('dpd-consulta-lista', 'value'), 
     Input('dpd-pozo-lista', 'value'),
     Input('dpd-column-list-y1', 'value'),
     Input('dpd-column-list-y2', 'value'),
     Input('ts-annotation', 'value'), 
     Input('dt_table_event', 'data'),
     Input('dpd-var-list-chart', 'data'),
     Input('inp-color-list-y1', 'value'),
     Input('inp-color-list-y2', 'value'),
     Input('cb_clear_data_line', 'value'),
     ])
def update_line_chart(n_clicks, file_name, well_name, column_list_y1, column_list_y2, show_annot, annot_data, var_list, color_y1, color_y2, clear_data):

    color_axis_y1 = dict(hex=color_y1)
    color_axis_y2 = dict(hex=color_y2)

    df = pd.DataFrame()
    query= ''
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    if 'btn_show_chart' in changed_id:
        con = sqlite3.connect(archivo)
        query = "SELECT * FROM VARIABLES"
        variables =pd.read_sql(query, con)
        query=''
        if file_name is not None:
            with open(os.path.join(QUERY_DIRECTORY, file_name)) as f:
                contenido = f.readlines()
            if contenido is not None:
                for linea in contenido:
                    query +=  linea 

                df =pd.read_sql(query, con)

                if well_name:
                    df = df[df['NOMBRE'].isin(well_name)]
                    
                df = df.sort_values(by="FECHA")
                
                if clear_data:
                    df = df[(df!=0)]

                if var_list:
                    for var in var_list:
                        selec_var=variables.loc[variables['NOMBRE']==var]
                        ecuacion = selec_var.iloc[0]['ECUACION']
                        titulo = selec_var.iloc[0]['TITULO']
                        evalu = eval(ecuacion)
                        df[titulo] = evalu
                i=1
                selec_unit = unidades.set_index(['VARIABLE'])
                print(color_axis_y1)
                for columnas_y1 in column_list_y1:
                    var_title = selec_unit.loc[columnas_y1]['GRAFICO']
                    var_unit = selec_unit.loc[columnas_y1]['UNIDAD']
                    var_color = selec_unit.loc[columnas_y1]['COLOR']
                    var_name = var_title + " " + var_unit

                    if color_axis_y1 == {'hex': '#1530E3'}:
                        color_axis_y1 = dict(hex=var_color)
                        
                    fig.add_trace(
                        go.Scatter(x=df['FECHA'],
                            y=df[columnas_y1],
                            name=var_name,
                            line_color=color_axis_y1["hex"],
                            yaxis= 'y'+ str(i)),
                        secondary_y=False,
                    )
                    i=+1

                for columnas_y2 in column_list_y2:
                    var_title = selec_unit.loc[columnas_y2]['GRAFICO']
                    var_unit = selec_unit.loc[columnas_y2]['UNIDAD']
                    var_name = var_title + " " + var_unit
                    var_color = selec_unit.loc[columnas_y2]['COLOR']

                    if color_axis_y2 == {'hex': '#1530E3'}:
                        color_axis_y2 = dict(hex=var_color)

                    fig.add_trace(
                        go.Scatter(x=df['FECHA'],
                            y=df[columnas_y2],
                            name=var_name,
                            line_color=color_axis_y2["hex"],
                            yaxis= 'y'+ str(i)),
                        secondary_y=True,
                    )
                    i=+1
                fig.update_xaxes(title_text="Fecha",showline=True, linewidth=2, linecolor='black', showgrid=False,)
                fig.update_yaxes(showline=True, linewidth=2, linecolor='black', showgrid=False,)
                fig.update_layout(
                    autosize=False,
                    hovermode='x unified',
                    height=700,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgb(240, 240, 240)',
                    margin=dict(
                        l=50,
                        r=50,
                        b=100,
                        t=100,
                        pad=4,
                    ),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    ),
                   )
                fig.update_xaxes(
                rangeslider_visible=True,
                    rangeselector=dict(
                        buttons=list([
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(count=1, label="YTD", step="year", stepmode="todate"),
                        dict(count=1, label="1y", step="year", stepmode="backward"),
                        dict(step="all")
                        ])
                    )
                )
                if show_annot:
                    dff = pd.DataFrame(annot_data)
                    for ind in dff.index:
                        fig.add_annotation(x=dff['FECHA'][ind], y=5,
                            text=dff['EVENTO'][ind],
                            showarrow=False,
                            bgcolor="#9DF5CE",
                            textangle=-90,
                            arrowhead=1)
        con.close()
    return fig

@app.callback(
    [Output('dpd-column-list-y1','options'),
     Output('dpd-column-list-y2','options')],
    [Input('dpd-consulta-lista', 'value'),
     Input('dpd-var-list-chart', 'value')])
def update_column_list(file_name, var_list):

    df = pd.DataFrame()
    columns = [{'label': i, 'value': i} for i in []]
    query= ''
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'dpd-consulta-lista' in changed_id or 'dpd-var-list-chart' in changed_id:
        con = sqlite3.connect(archivo)
        query = "SELECT * FROM VARIABLES"
        variables =pd.read_sql(query, con)
        query=''
        if file_name:
            with open(os.path.join(QUERY_DIRECTORY, file_name)) as f:
                contenido = f.readlines()
                for linea in contenido:
                    query +=  linea
                df =pd.read_sql(query, con)

            if var_list is not None:
                for var in var_list:
                    selec_var=variables.loc[variables['NOMBRE']==var]
                    ecuacion = selec_var.iloc[0]['ECUACION']
                    titulo = selec_var.iloc[0]['TITULO']
                    evalu = eval(ecuacion)
                    df[titulo] = evalu

            columns = [{'label': i, 'value': i} for i in df.columns]
        con.close()

    return columns, columns

@app.callback(
    Output('save_message_linechart','children'),
    [Input('btn_save_linechart', 'n_clicks'),
    Input('dpd-consulta-lista', 'value'),
    Input('dpd-column-list-y1', 'value'),
    Input('dpd-column-list-y2', 'value'),
    Input('inp-ruta-linechart', 'value'),
    Input('dpd-var-list-chart', 'value'),
    Input('inp-color-list-y1', 'value'), 
    Input('inp-color-list-y2', 'value'),
    Input('ts-annotation', 'value'),
    ]) 
def save_linechart(n_clicks, consulta, datos_y1, datos_y2, file_name, var_list, color_y1, color_y2, text_annot ):
    mensaje=''
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'btn_save_linechart' in changed_id:
        data = {}
        data['grafico'] = []
        data['grafico'].append({
            'consulta': consulta,
            'datos_y1': datos_y1,
            'datos_y2': datos_y2,
            'var_list': var_list,
            'color_y1': color_y1,
            'color_y2': color_y2,
            'annotation': text_annot,
            })
        with open(CHART_DIRECTORY+file_name, 'w') as file:
            json.dump(data, file, indent=4)
        mensaje = 'Archivo guardado'
    return mensaje

@app.callback( [Output('inp-ruta-linechart', 'value'),
                Output('dpd-consulta-lista', 'value'),
                Output('dpd-column-list-y1', 'value'),
                Output('dpd-column-list-y2', 'value'),
                Output('dpd-var-list-chart', 'value'),
                Output('inp-color-list-y1', 'value'),
                Output('inp-color-list-y2', 'value'),
                Output('ts-annotation', 'value'),
                ],
              [Input('btn_open_linechart', 'filename'),
              Input('btn_open_linechart', 'contents')]
              )
def open_linechart( list_of_names, list_of_contents):
    archivo = list_of_names
    consulta=[]
    datos_y1=[]
    datos_y2=[]
    var_list=[]
    color_y1=[]
    color_y2=[]
    text_annot=[]

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'btn_open_linechart' in changed_id:

        if list_of_names is not None:
            archivo = list_of_names
            with open(CHART_DIRECTORY+archivo) as file:
                data = json.load(file)
                for drop_values   in data['grafico']:
                    consulta = str(drop_values['consulta'])
                    datos_y1 = drop_values['datos_y1']
                    datos_y2 = drop_values['datos_y2']
                    var_list = drop_values['var_list']
                    color_y1 = drop_values['color_y1']
                    color_y2 = drop_values['color_y2']
                    text_annot = drop_values['annotation']
                    
    return archivo, consulta, datos_y1, datos_y2, var_list, color_y1, color_y2, text_annot