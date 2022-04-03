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
from sklearn.preprocessing import PolynomialFeatures 
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline

from app import app 
from library import reform_df, search_unit, search_calcv, search_list, format_coefs

#Variable con la ruta para salvar los querys
QUERY_DIRECTORY = "./querys"

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

#Listado de variables calculadas
query = "SELECT NOMBRE FROM VARIABLES"
var_list =pd.read_sql(query, con)
var_list = var_list.sort_values('NOMBRE')['NOMBRE'].unique()

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
                            id='dpd-query-list-scatter',
                            options=[
                                {'label': i, 'value': i} for i in files
                            ],
                            clearable=False
                        ),
                    ], width={"size": 4, "offset": 1}),
                    dbc.Col([
                        html.Label(['Pozo:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                            id='dpd-well-list-scatter',
                            options=[{'label': i, 'value': i} for i in well_list],
                            clearable=False,
                            multi=True
                        ),
                    ], width={"size": 4, "offset": 0}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button(html.Span(["Mostrar ", html.I(className="fas fa-chart-bar ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                         id="btn_show_scatterchart", color="success", className="mr-3"),
                    ]),
                ]),
                html.Br(),
            ], style={"background-color": "#F9FCFC"},),
        ], width={"size": 6, "offset": 0}),
        dbc.Col([
            dbc.Card([
                dbc.Row([
                    dbc.Col([
                        html.Label(['Nombre Plantilla:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dbc.Input(id="inp-ruta-scatterchart", placeholder="Type something...", type="text", style={'backgroundColor':'white'}),
                    ], width={"size": 3, "offset": 1}),
                     dbc.Col([
                        html.Br(),
                        dcc.Upload(
                            dbc.Button(html.Span(["Abrir ", html.I(className="fas fa-upload ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                              n_clicks=0, color="primary", className="mr-3"),
                            id='btn_open_scatterchart',
                            multiple=False
                        ),
                    ], width={"size": 1, "offset": 0}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button(html.Span(["Grabar ", html.I(className="fas fa-save ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                         id="btn_save_scatterchart", n_clicks=0, color="primary", className="mr-3"),
                        html.Div(id="save_message_scatter"),
                    ], width={"size": 2, "offset": 1}),
                ]),
                html.Br(),
            ], style={"background-color": "#F9FCFC"},),
        ], width={"size": 6, "offset": 0}),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dac.Box([
                    dac.BoxHeader(
                        collapsible = False,
                        closable = False,
                        title="Grafico de Dispersión"
                    ),
                    dac.BoxBody(
                        dcc.Loading(
                            dcc.Graph(id='cht-scatter-chart', style={"width": "100%"}),
                        ),
                    ),
                ],
                color='primary',
                solid_header=True,
                elevation=4,
                width=12,
            ),
        ], width=9),
        dbc.Col([
            dac.Box([
                dac.BoxHeader(
                    collapsible = False,
                    closable = False,
                    title="Opciones"
                ),
                dac.BoxBody([
                        dcc.Checklist(
                            id='ckl-zoom-scatter-data',
                            options=[
                                {'label': ' Mantener Zoom', 'value': 'CERO'},
                            ],
                            value=[],
                        ),
                        html.Br(),
                        html.Label(['Eje X'],style={'font-weight': 'bold', "text-align": "left"}),
                        html.Label(['Datos:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                            id='dpd-column-list-x-scatter',
                            clearable=False,
                            multi=False
                        ),
                        html.Label(['Eje Y'],style={'font-weight': 'bold', "text-align": "left"}),
                        html.Label(['Datos:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                            id='dpd-column-list-y-scatter',
                            clearable=False,
                            multi=False
                        ),
                        html.Label(['Variable Calculadas:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                            id='dpd-var-list-scatterchart',
                            options=[{'label': i, 'value': i} for i in var_list],
                            clearable=False,
                            multi=True,
                        ),
                        
                    ]),
                ],
                color='primary',
                solid_header=True,
                elevation=4,
                width=12,
                style={"background-color": "#F9FCFC"},
            ),
            dac.Box([
                dac.BoxHeader(
                    collapsible = False,
                    closable = False,
                    title="Estadísticas"
                ),
                dac.BoxBody([
                        
                        html.Br(),
                        html.Label(['Regresión:'],style={'font-weight': 'bold', "text-align": "left"}),
                        daq.ToggleSwitch(
                            id='ts-statistic',
                            value=False,
                            label='Mostrar Linea Tendencia',
                            labelPosition='top'
                        ),
                        html.Br(),
                        html.Label(['Grado del Polinomio:'],style={'font-weight': 'bold', "text-align": "center"}),
                        dcc.Slider(id='PolyFeat',
                            min=1,
                            max=6,
                            marks={i: '{}'.format(i) for i in range(10)},
                            value=1,
                        ),
                        html.Br(),
                        html.Label(['Resultados:'],style={'font-weight': 'bold', "text-align": "left"}),
                        html.Label(['Ecuacion:'],style={'font-weight': 'bold', "text-align": "left"}),
                        html.Div(id="ecuacion"),
                        html.Label(['Coeficientes:'],style={'font-weight': 'bold', "text-align": "left"}),
                        html.Div(id="coeficientes"),
                        html.Div(id="r_squared"),
                    ]),
                ],
                color='primary',
                solid_header=True,
                elevation=4,
                width=12,
                style={"background-color": "#F9FCFC"},
            ),
        ], width=3),
    ]),
    dbc.Modal(
        [
            dbc.ModalHeader("Plantilla guardada"),
        ],
        id="modal_scatter",
        is_open=False,
    ),
    dbc.Modal(
        [
            dbc.ModalHeader("error"),
        ],
        id="modal_error",
        is_open=False,
    ),
])

@app.callback(
    [Output('cht-scatter-chart','figure'),
     Output('coeficientes','children'),
     Output('ecuacion','children'),
     Output('r_squared','children'),
     Output("modal_error", "children"),
     Output("modal_error", "is_open"),
    ], 
    [Input("btn_show_scatterchart", "n_clicks"),
     Input('dpd-query-list-scatter', 'value'), 
     Input('dpd-well-list-scatter', 'value'),
     Input('dpd-column-list-x-scatter', 'value'),
     Input('dpd-column-list-y-scatter', 'value'),
     Input('dpd-var-list-scatterchart', 'value'),
     Input("PolyFeat", "value"),
     Input('ts-statistic', 'value'),
     Input('ckl-zoom-scatter-data','value'),
     ],
     [State("modal_error", "is_open"),
    State("modal_error", "children"),
    State('cht-scatter-chart', 'relayoutData')])
def update_scatter_chart(n_clicks, file_name, well_name, column_list_x, column_list_y, var_list, nFeatures, trendline, zoom_data, is_open, children, relayout_data):

    df = pd.DataFrame()
    query= ''
    results=''
    pd_results = pd.DataFrame()
    dff = pd.DataFrame()
    results = {}
    r_squared = ''
    equation = ''
    abierto = False
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    fig = {}
    
    if 'btn_show_scatterchart' in changed_id:
        con = sqlite3.connect(archivo)
        query = "SELECT * FROM VARIABLES"
        variables =pd.read_sql(query, con)
        query= ''
        test_results=''

        if file_name:
            with open(os.path.join(QUERY_DIRECTORY, file_name)) as f:
                contenido = f.readlines()
            if contenido:
                try:
                    if well_name:
                        for linea in contenido:
                            query +=  linea 
                        df =pd.read_sql(query, con)
                        df =df.sort_values("FECHA")
                        df = df[df['NOMBRE'].isin(well_name)]

                        xaxis_name, var_color = search_unit(unidades, column_list_x)
                        yaxis_name, var_color = search_unit(unidades, column_list_y)

                        if column_list_x and column_list_y:
                            if var_list is not None:
                                for columna in df.columns:
                                    if columna != 'FECHA' and columna != 'NOMBRE':
                                        df[columna] = pd.to_numeric(df[columna])

                                for var in var_list:
                                    requisitos_list, titulo, ecuacion = search_calcv( archivo, var)

                                    if search_list(requisitos_list, df.columns.tolist()):
                                        evalu = eval(ecuacion)
                                        df[titulo] = evalu

                            fig = px.scatter(x=df[column_list_x],
                                    y=df[column_list_y], color=df['NOMBRE'])
                
                            if 'xaxis.range[0]' in relayout_data and zoom_data:
                                fig['layout']['xaxis']['range'] = [
                                    relayout_data['xaxis.range[0]'],
                                    relayout_data['xaxis.range[1]']
                                ]
                                fig['layout']['yaxis']['range'] = [
                                    relayout_data['yaxis.range[0]'],
                                    relayout_data['yaxis.range[1]']
                                ]
                                
                                #filtra los datos de acuerdo al zoom realizado
                                df = df[(df[column_list_x] >= relayout_data['xaxis.range[0]']) & (df[column_list_x] <= relayout_data['xaxis.range[1]'])]
                                df = df[(df[column_list_y] >= relayout_data['yaxis.range[0]']) & (df[column_list_y] <= relayout_data['yaxis.range[1]'])]
    
                            fig.update_xaxes(title_text=xaxis_name,showline=True, linewidth=2, linecolor='black', showgrid=False,)
                            fig.update_yaxes(title_text=yaxis_name,showline=True, linewidth=2, linecolor='black', showgrid=False,)
                            fig.update_layout(
                                autosize=False,
                                paper_bgcolor='rgba(0,0,0,0)',
                                height=700,
                                plot_bgcolor='rgb(240, 240, 240)',
                                margin=dict(
                                    l=50,
                                    r=50,
                                    b=100,
                                    t=100,
                                    pad=4,
                                ),
                            )
                            fig.update_layout(legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=1.02,
                                xanchor="right",
                                x=1
                            ))
                            if trendline:
                                try:
                                    #Elimina los valores NaN
                                    df = f = df[df[column_list_x].notna()]
                                    df = f = df[df[column_list_y].notna()]

                                    x=df[column_list_x]
                                    y=df[column_list_y]
                                    coeffs = np.polyfit(x, y, nFeatures)
                                    p7 = np.poly1d(np.polyfit(x, y,  nFeatures))
                                    xp = np.linspace(min(x), max(x), 300)

                                    results = coeffs.tolist()
                                    results = [round(num, 2) for num in results]
                                    equation = format_coefs(results)

                                    # r-squared
                                    p = np.poly1d(coeffs)
                                    # fit values, and mean
                                    yhat = p(x)                         # or [p(z) for z in x]
                                    ybar = np.sum(y)/len(y)          # or sum(y)/len(y)
                                    ssreg = np.sum((yhat-ybar)**2)   # or sum([ (yihat - ybar)**2 for yihat in yhat])
                                    sstot = np.sum((y - ybar)**2)    # or sum([ (yi - ybar)**2 for yi in y])
                                    r_squared = 'R2 = {} '.format(ssreg / sstot)

                                    fig.add_traces(go.Scatter(x=xp, y=p7(xp), mode='lines', name = 'Tendencia'))
                                except Exception  as e:
                                    abierto = True
                                    children = [dbc.ModalHeader("Error"),
                                        dbc.ModalBody(
                                            html.H6('Error de convergencia: {}'.format(e), style={'textAlign': 'center', 'padding': 10}),
                                        ),
                                    ]
                except Exception  as e:
                    abierto = True
                    children = [dbc.ModalHeader("Error"),
                        dbc.ModalBody(
                            html.H6('Probelmas con la consulta, error: {}'.format(e), style={'textAlign': 'center', 'padding': 10}),
                        ),
                    ]
        con.close()

    return fig, html.Ul([html.Li(x) for x in results]), equation, r_squared, children, abierto


@app.callback(
    [Output('dpd-column-list-x-scatter','options'),
     Output('dpd-column-list-y-scatter','options')],
    [Input('dpd-query-list-scatter', 'value'),
    Input('dpd-var-list-scatterchart', 'value')])
def update_column_list(file_name, var_list):

    df = pd.DataFrame()
    columns = [{'label': i, 'value': i} for i in []]

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'dpd-query-list-scatter' in changed_id or 'dpd-var-list-scatterchart' in changed_id:
        con = sqlite3.connect(archivo)
        query= ''
        if file_name:
            with open(os.path.join(QUERY_DIRECTORY, file_name)) as f:
                contenido = f.readlines()
                for linea in contenido:
                    query +=  linea

                #Filtrar solo la primera fila
                query += " LIMIT 1"
                df =pd.read_sql(query, con)
                if var_list is not None:
                    for columna in df.columns:
                        if columna != 'FECHA' and columna != 'NOMBRE':
                            df[columna] = pd.to_numeric(df[columna])

                    for var in var_list:
                        requisitos_list, titulo, ecuacion = search_calcv( archivo, var)

                        if search_list(requisitos_list, df.columns.tolist()):
                            evalu = eval(ecuacion)
                            df[titulo] = evalu
                if  df.columns[2]=='FECHA':
                    columns=[{'label': i, 'value': i} for i in df.columns[3:]]
                else:
                    columns=[{'label': i, 'value': i} for i in df.columns[2:]]

        con.close()

    return columns, columns

@app.callback(
    Output('modal_scatter','is_open'),
    [Input('btn_save_scatterchart', 'n_clicks'),
    Input('dpd-query-list-scatter', 'value'),
    Input('dpd-column-list-x-scatter', 'value'),
    Input('dpd-column-list-y-scatter', 'value'),
    Input('inp-ruta-scatterchart', 'value'),
    Input('dpd-var-list-scatterchart', 'value'),
    Input('ts-statistic','value'),
    Input("PolyFeat", "value"),
    State('modal_scatter','is_open')]) 
def save_scatterchart(n_clicks, consulta, datos_y1, datos_y2, file_name, var_list, trend_type, nFeatures, is_open ):
    mensaje=''
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'btn_save_scatterchart' in changed_id:
        if file_name:
            data = {}
            data['grafico'] = []
            data['grafico'].append({
                'consulta': consulta,
                'datos_y1': datos_y1,
                'datos_y2': datos_y2,
                'var_list': var_list,
                'trend_line': trend_type,
                'nFeatures' : nFeatures,
                })
            with open(CHART_DIRECTORY+file_name, 'w') as file:
                json.dump(data, file, indent=4)
            is_open =True
    return is_open

@app.callback( [Output('inp-ruta-scatterchart', 'value'),
                Output('dpd-query-list-scatter', 'value'),
                Output('dpd-column-list-x-scatter', 'value'),
                Output('dpd-column-list-y-scatter', 'value'),
                Output('dpd-var-list-scatterchart', 'value'),
                Output('ts-statistic', 'value'),
                Output("PolyFeat", "value"),
                ],
              [Input('btn_open_scatterchart', 'filename'),
              Input('btn_open_scatterchart', 'contents')]
              )
def open_scatterchart( list_of_names, list_of_contents):
    archivo = list_of_names
    consulta=[]
    datos_y1=[]
    datos_y2=[]
    var_list=[]
    trend_line=False
    nFeatures=1

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'btn_open_scatterchart' in changed_id:
        if list_of_names is not None:
            archivo = list_of_names
            with open(CHART_DIRECTORY+archivo) as file:
                data = json.load(file)
                for drop_values   in data['grafico']:
                    consulta = str(drop_values['consulta'])
                    datos_y1 = drop_values['datos_y1']
                    datos_y2 = drop_values['datos_y2']
                    var_list = drop_values['var_list']
                    trend_line = drop_values['trend_line']
                    nFeatures = drop_values['nFeatures']

    return archivo, consulta, datos_y1, datos_y2, var_list, trend_line, nFeatures