import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Row import Row
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash_html_components.Br import Br
from scipy.interpolate import griddata
import plotly.graph_objects as go
import plotly.express as px
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
from datetime import datetime, tzinfo, timezone, timedelta, date
from collections import OrderedDict
import base64
import os

from app import app 

#Variable con la ruta para salvar los querys
QUERY_DIRECTORY = "./querys"

#Lee el archivo de configuracion
configuracion = configparser.ConfigParser()

#Variable con la ruta para salvar los querys
QUERY_DIRECTORY = "./querys"

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

#Listado de query
pathway = './querys'
files = [f for f in listdir(pathway) if isfile(join(pathway, f))]

file_name = ''

welldat = pd.read_csv('./datasets/survey_data.csv')
x, y, z = welldat.x, welldat.y, welldat.depth
#xi = np.linspace(min(x), max(x),200, retstep=False)
#yi = np.linspace(min(y), max(y),200, retstep=False)

xi = np.arange(x.min(),x.max(),(x.max()-x.min())/100)
yi=np.arange(y.min(),y.max(),(y.max()-y.min())/100)

xi, yi = np.meshgrid(xi, yi)

layout = html.Div([
    dbc.Row([
        dbc.Col([
            html.Label(['Consulta:'],style={'font-weight': 'bold', "text-align": "left"}),
            dcc.Dropdown(
                id='dpd-query-list',
                options=[
                     {'label': i, 'value': i} for i in files
                 ],
                clearable=False
            ),
        ], width=2),
        dbc.Col([
            html.Label(['Fecha: '],style={'font-weight': 'bold', "text-align": "left"}),
            dcc.DatePickerSingle(
                id='dtp_fecha',
                date=date.today(),
                display_format='YYYY-MM-DD',
                style={'backgroundColor':'white'},
            )
        ], width=3),
        dbc.Col([
            html.Br(),
            dbc.Button("Mostrar Grafico", id="btn_show_chart", color="success", className="mr-3"),
        ], width=1.5),
        dbc.Col([
            html.Br(),
            dbc.Button("Exportar Imagen", id="btn_export_img", color="warning", className="mr-3"),
        ]),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.Label(['Gráfico de Contorno'],style={'font-weight': 'bold', "text-align": "left"})),
                dbc.CardBody([
                    dbc.Spinner(
                        dcc.Graph(id='cht-contour-chart'),
                    ),
                ])
            ]),
        ], width=9),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.Label(['Opciones'],style={'font-weight': 'bold', "text-align": "left"})),
                dbc.CardBody([
                    html.Label(['Nombre del Gráfico'],style={'font-weight': 'bold', "text-align": "left"}),
                    dbc.Input(id="inp_chart_name", placeholder="Type something...", type="text", style={'backgroundColor':'white'}),
                    html.Br(),
                    html.Label(['Datos:'],style={'font-weight': 'bold', "text-align": "left"}),
                    dcc.Dropdown(
                        id='dpd-data-lists',
                        clearable=False,
                        multi=False,
                    ),
                ])
            ]),
        ], width=3),
    ]),
])

@app.callback(
    Output('cht-contour-chart','figure'),
    [Input("btn_show_chart", "n_clicks"),
     Input('dpd-query-list', 'value'), 
     Input('dpd-data-lists', 'value'),
     Input('dtp_fecha', 'date'),
     Input('inp_chart_name', 'value')])
def update_contour_map(n_clicks, file_name, columns_list, dtp_fecha, chart_title):

    data_results = pd.DataFrame()
    quer= ''
    fecha = str(dtp_fecha)
    df = pd.DataFrame()

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    fig = go.Figure()
    if 'btn_show_chart' in changed_id:
        con = sqlite3.connect(archivo)
        if file_name is not None:
            with open(os.path.join(QUERY_DIRECTORY, file_name)) as f:
                contenido = f.readlines()
            if contenido is not None:
                if fecha is not None:
                    for linea in contenido:
                        query =  linea + " WHERE date(FECHA)='"+fecha+"' ORDER BY FECHA"

                data_results =pd.read_sql(query, con)

                z = data_results[columns_list]

                # grid N data with cubic interpolation method
                zi = griddata((x,y),z,(xi,yi),method='cubic')

                fig = go.Figure(data = go.Contour(z=zi, contours=dict(
                            coloring ='heatmap',
                            showlabels = True, # show labels on contours
                            labelfont = dict( # label font properties
                                size = 12,
                                color = 'white',
                            ))))
                # Update plot sizing
                fig.update_layout(
                    width=1000,
                    height=750,
                    autosize=False,
                    margin=dict(t=0, b=0, l=0, r=0),
                )

                # Update 3D scene options
                fig.update_scenes(
                    aspectratio=dict(x=1, y=1, z=0.7),
                    aspectmode="manual"
                )
                # button_layer_1_height = 1.08
                button_layer_1_height = 1.12
                button_layer_2_height = 1.065

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

                fig.update_layout(
                    annotations=[
                        dict(text="Escala<br>Colores", x=0, xref="paper", y=1.1, yref="paper",
                                            align="left", showarrow=False),
                        dict(text="Reversar<br>Escala Colores", x=0.6, xref="paper", y=1.1,
                                            yref="paper", align="left", showarrow=False),
                    ])
                
    return fig

@app.callback(
    [Output('dpd-data-lists','options'),
    Output('dpd-data-lists','value')],
    [Input('dpd-query-list', 'value')])
def update_column_list(file_name):

    data_results = pd.DataFrame()
    columns = [{'label': i, 'value': i} for i in []]
    quer= ''
    valor=[]
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'dpd-query-list' in changed_id:
        con = sqlite3.connect(archivo)
        if file_name is not None:
            with open(os.path.join(QUERY_DIRECTORY, file_name)) as f:
                contenido = f.readlines()
                for linea in contenido:
                    query =  linea
                data_results =pd.read_sql(query, con)
                data_results =data_results.drop(['index', 'NOMBRE', 'FECHA'], axis=1)
                columns = [{'label': i, 'value': i} for i in data_results.columns]
                valor.append(data_results.columns[0])
    return columns, valor