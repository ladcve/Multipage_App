import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Row import Row
import dash_daq as daq
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_admin_components as dac
from scipy.interpolate import griddata
import plotly.graph_objects as go
import plotly.express as px
import dash_table
import sqlite3
import configparser
import json
import sys
import os.path
import os
from os import listdir
from os.path import isfile, join
import numpy as np
import pandas as pd
from datetime import datetime, tzinfo, timezone, timedelta, date
from collections import OrderedDict
import base64
import os

from app import app 
from library import search_unit, search_list, search_calcv

#Variable con la ruta para salvar los querys
QUERY_DIRECTORY = "./querys"
CHART_DIRECTORY = "./template/"

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

query = "SELECT NOMBRE FROM VARIABLES"
var_list =pd.read_sql(query, con)
var_list = var_list.sort_values('NOMBRE')['NOMBRE'].unique()

#Listado de query
pathway = './querys'
files = [f for f in listdir(pathway) if isfile(join(pathway, f))]

file_name = ''

layout = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.Row([
                    dbc.Col([
                        html.Label(['Consulta:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                            id='dpd-query-list-contour',
                            options=[
                                {'label': i, 'value': i} for i in files
                            ],
                            clearable=False
                        ),
                    ], width={"size": 4, "offset": 1}),
                    dbc.Col([
                        html.Label(['Fecha: '],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.DatePickerSingle(
                            id='dtp_fecha',
                            date=date.today(),
                            display_format='YYYY-MM-DD',
                            style={'backgroundColor':'white'},
                        )
                    ], width={"size": 2, "offset": 0}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button(html.Span(["Mostrar ", html.I(className="fas fa-map ml-1")],style={'font-size':'1.5em','text-align':'center'}), 
                        id="btn_show_chart", color="success", className="mr-3"),
                    ], width={"size": 1, "offset": 1}),
                ]),
                html.Br(),
            ], style={"background-color": "#F9FCFC"},),
        ], width={"size": 7, "offset": 0}),
        dbc.Col([
            dbc.Card([
                dbc.Row([
                    dbc.Col([
                        html.Label(['Nombre Plantilla:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dbc.Input(id="inp-ruta-map", placeholder="Type something...", type="text", style={'backgroundColor':'white'}),
                    ], width={"size": 3, "offset": 1}),
                     dbc.Col([
                        html.Br(),
                        dcc.Upload(
                            dbc.Button(
                                html.Span(["Abrir ", html.I(className="fas fa-upload ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                                n_clicks=0, color="primary", className="mr-3"
                            ),
                            id='btn_open_contour',
                            multiple=False
                        ),
                    ], width={"size": 2, "offset": 0}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button(html.Span(["Grabar ", html.I(className="fas fa-save ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                            id="btn_save_map", 
                            n_clicks=0, 
                            color="primary", 
                            className="mr-3"
                        ),
                        html.Div(id="save_message_contour"),
                    ], width={"size": 3, "offset": 1}),
                ]),
                html.Br(),
            ], style={"background-color": "#F9FCFC"},),
        ], width={"size": 5, "offset": 0}),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dac.Box([
                    dac.BoxHeader(
                        collapsible = False,
                        closable = False,
                        title="Mapa de Contorno"
                    ),
                    dac.BoxBody([
                        dbc.Spinner(
                            dcc.Graph(id='cht-contour-chart', style={"width": "100%"}),
                        ),
                    ]),	
                ],
                color='primary',
                solid_header=True,
                elevation=4,
                width=12
            ),
        ], width=9),
        dbc.Col([
            dac.Box([
                    dac.BoxHeader(
                        collapsible = False,
                        closable = False,
                        title="Marcadores Estratgráficos"
                    ),
                    dac.BoxBody([     
                        html.Label(['Nombre del Gráfico'],style={'font-weight': 'bold', "text-align": "left"}),
                        dbc.Input(id="inp_map_name", placeholder="Type something...", inputMode="numeric", type="text", style={'backgroundColor':'white'}),
                        html.Br(),
                        html.Label(['Datos:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                            id='dpd-data-lists',
                            clearable=False,
                            multi=False,
                        ),
                        html.Br(),
                        html.Label(['Muestreo: '],style={'font-weight': 'bold', "text-align": "left"}),
                        dbc.Input(id="inp_sample", placeholder="Type something...", value=300, 
                          type="number", min=50, max=450, style={'backgroundColor':'white'}),
                        html.Br(),
                        daq.ToggleSwitch(
                            id='ts-emtpyspace',
                            value=True,
                            label='Rellenar Espacio',
                            labelPosition='top'
                        ),
                        html.Br(),  
                        html.Label(['Variable Calculadas:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                            id='dpd-var-list-contour',
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
        ], width=3),
    ]),
    dbc.Modal(
        [
            dbc.ModalHeader("Plantilla Salvada"),
        ],
        id="modal_map",
        is_open=False,
    ),
])

@app.callback(
    Output('cht-contour-chart','figure'),
    [Input("btn_show_chart", "n_clicks"),
     Input('dpd-query-list-contour', 'value'), 
     Input('dpd-data-lists', 'value'),
     Input('dtp_fecha', 'date'),
     Input('inp_map_name', 'value'),
     Input('dpd-var-list-contour', 'value'),
     Input('ts-emtpyspace', 'value'),
     Input('inp_sample', 'value')])
def update_contour_map(n_clicks, file_name, columns_list, dtp_fecha, chart_title, var_list, emtpy_space, sample):

    df = pd.DataFrame()
    query= ''
    fecha = str(dtp_fecha)
    df = pd.DataFrame()

    welldat = pd.read_csv('./datasets/survey_data.csv')
    x, y, z = welldat.x, welldat.y, welldat.depth

    if sample is not None:
        #xi = np.linspace(min(x), max(x),sample, retstep=False)
        #yi = np.linspace(min(y), max(y),sample, retstep=False)
        xi = np.arange(x.min(),x.max(),(x.max()-x.min())/int(sample))
        yi=np.arange(y.min(),y.max(),(y.max()-y.min())/int(sample))
        xi, yi = np.meshgrid(xi, yi)

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    fig = go.Figure()
    if 'btn_show_chart' in changed_id:
        con = sqlite3.connect(archivo)
        query= ''
        if file_name is not None:
            with open(os.path.join(QUERY_DIRECTORY, file_name)) as f:
                contenido = f.readlines()
            if contenido is not None:
                if fecha is not None:
                    for linea in contenido:
                        query +=  linea

                    if query.find("WHERE")>-1 or query.find("where")>-1:
                        if query.find("A.")>-1:
                            query += " AND date(A.FECHA)='"+fecha+"' ORDER BY A.FECHA"
                        else:
                            query += " AND date(FECHA)='"+fecha+"' ORDER BY FECHA"
                    else:
                        if query.find("A.")>-1:
                            query += " WHERE date(A.FECHA)='"+fecha+"' ORDER BY A.FECHA"
                        else:
                             query += " WHERE date(FECHA)='"+fecha+"' ORDER BY FECHA"
                
                df =pd.read_sql(query, con)

                if var_list:
                    for columna in df.columns:
                        if columna != 'FECHA' and columna != 'NOMBRE':
                            df[columna] = pd.to_numeric(df[columna])

                    for var in var_list:
                        requisitos_list, titulo, ecuacion = search_calcv( archivo, var)
                        if search_list(requisitos_list, df.columns.tolist()):
                            df[titulo] =eval(ecuacion)

                z = df[columns_list]
                if len(df)>0:
                    # grid N data with cubic interpolation method
                    zi = griddata((x,y),z,(xi,yi),method='cubic')

                    fig = go.Figure(data = go.Contour(z=zi, connectgaps=emtpy_space, contours=dict(
                                coloring ='heatmap',
                                showlabels = True, # show labels on contours
                                labelfont = dict( # label font properties
                                    size = 12,
                                    color = 'white',
                                ))))
                    # Update plot sizing
                    fig.update_layout(
                        width=1200,
                        height=750,
                        autosize=False,
                        margin=dict(t=0, b=0, l=0, r=150),
                    )

                    # Update 3D scene options
                    fig.update_scenes(
                        aspectratio=dict(x=1, y=1, z=0.7),
                        aspectmode="manual"
                    )
                    # button_layer_1_height = 1.08
                    button_layer_1_height = 1.12
                    button_layer_2_height = 1.1

                    fig.update_layout(
                        updatemenus=[
                            dict(
                                buttons=list([
                                    dict(
                                        args=["colorscale", "Heatmap"],
                                        label="heatmap",
                                        method="restyle"
                                    ),
                                    dict(
                                        args=["colorscale", "Viridis"],
                                        label="Viridis",
                                        method="restyle"
                                    ),
                                    dict(
                                        args=["colorscale", "Cividis"],
                                        label="Cividis",
                                        method="restyle"
                                    ),
                                    dict(
                                        args=["colorscale", "Blues"],
                                        label="Blues",
                                        method="restyle"
                                    ),
                                    dict(
                                        args=["colorscale", "Greens"],
                                        label="Greens",
                                        method="restyle"
                                    ),
                                ]),
                                type = "buttons",
                                direction="right",
                                pad={"r": 10, "t": 10},
                                showactive=True,
                                x=0.1,
                                xanchor="left",
                                y=button_layer_1_height,
                                yanchor="top"
                            ),
                            dict(
                                buttons=list([
                                    dict(
                                        args=["reversescale", False],
                                        label="False",
                                        method="restyle"
                                    ),
                                    dict(
                                        args=["reversescale", True],
                                        label="True",
                                        method="restyle"
                                    ),
                                    dict(
                                        args=["type", "surface"],
                                        label="3D Surface",
                                        method="restyle"
                                    ),
                                    dict(
                                        args=["type", "heatmap"],
                                        label="Contorno",
                                        method="restyle"
                                    )
                                ]),
                                type = "buttons",
                                direction="right",
                                pad={"r": 10, "t": 10},
                                showactive=True,
                                x=0.7,
                                xanchor="left",
                                y=button_layer_1_height,
                                yanchor="top"
                            ),
                        ]
                    )
                    fig.update_layout(modebar_orientation="v"),
                    fig.update_layout(
                        annotations=[
                            dict(text="Escala<br>Colores", x=0, xref="paper", y=1.1, yref="paper",
                                                align="left", showarrow=False),
                            dict(text="Reversar<br>Escala Colores y Forma", x=0.6, xref="paper", y=1.1,
                                                yref="paper", align="left", showarrow=False),
                        ])
                
    return fig

@app.callback(
    Output('dpd-data-lists','options'),
    [Input('dpd-query-list-contour', 'value'),
     Input('dpd-var-list-contour', 'value')])
def update_column_list(file_name, var_list):

    df = pd.DataFrame()
    columns = [{'label': i, 'value': i} for i in []]
    query= ''
    valor=[]
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'dpd-query-list-contour' in changed_id or 'dpd-var-list-contour' in changed_id:
        con = sqlite3.connect(archivo)
        query=''
        if file_name:
            with open(os.path.join(QUERY_DIRECTORY, file_name)) as f:
                contenido = f.readlines()
                for linea in contenido:
                    query +=  linea

                #Filtrar solo la primera fila
                query += " LIMIT 1"

                df =pd.read_sql(query, con)

            if var_list:
                for columna in df.columns:
                    if columna != 'FECHA' and columna != 'NOMBRE':
                        df[columna] = pd.to_numeric(df[columna])

                for var in var_list:
                    requisitos_list, titulo, ecuacion = search_calcv( archivo, var)
                    if search_list(requisitos_list, df.columns.tolist()):
                        df[titulo] =eval(ecuacion)

            #Valilda si la columna index existe en el dataframe
            if 'index' in df:
                df =df.drop(['index', 'NOMBRE', 'FECHA'], axis=1)
            else:
                df =df.drop(['NOMBRE', 'FECHA'], axis=1)

            columns = [{'label': i, 'value': i} for i in df.columns]

        con.close()

    return columns

@app.callback(
    Output('modal_map','is_open'),
    [Input('btn_save_map', 'n_clicks'),
    Input('dpd-query-list-contour', 'value'),
    Input('dpd-data-lists', 'value'),
    Input('inp-ruta-map', 'value'),
    Input('dpd-var-list-contour', 'value'),
    Input('inp_sample','value'),
    Input('ts-emtpyspace', 'value'),
    State('modal_map', 'is_open')]) 
def save_contour(n_clicks, consulta, datos_y1, file_name, var_list, sample, emptyspace, is_open ):
    mensaje=''
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'btn_save_map' in changed_id:
        data = {}
        data['grafico'] = []
        data['grafico'].append({
            'consulta': consulta,
            'datos_y1': datos_y1,
            'var_list': var_list,
            'sample': sample,
            'emptyspace': emptyspace,})
        if file_name:
            with open(CHART_DIRECTORY+file_name, 'w') as file:
                json.dump(data, file, indent=4)
            is_open = True
    return is_open

@app.callback( [Output('inp_map_name', 'value'),
                Output('dpd-query-list-contour', 'value'),
                Output('dpd-data-lists', 'value'),
                Output('dpd-var-list-contour', 'value')],
              [Input('btn_open_contour', 'filename'),
              Input('btn_open_contour', 'contents')]
              )
def open_map( list_of_names, list_of_contents):
    archivo = list_of_names
    consulta=[]
    datos_y1=[]
    var_list=[]
    sample=[]
    emptyspace=[]
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'btn_open_contourmap' in changed_id:
        if list_of_names is not None:
            print(list_of_names)
            archivo = list_of_names
            with open(CHART_DIRECTORY+archivo) as file:
                data = json.load(file)
                for drop_values   in data['grafico']:
                    consulta = str(drop_values['consulta'])
                    datos_y1 = drop_values['datos_y1']
                    var_list = drop_values['var_list']
                    sample = drop_values['sample']
                    emptyspace = drop_values['emptyspace']
    return archivo, consulta, datos_y1, var_list