import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Row import Row
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ALL, MATCH
import plotly.graph_objects as go
import dash_admin_components as dac
from plotly.subplots import make_subplots
import dash_table
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
import os, fnmatch
import lasio.examples
from plotly.subplots import make_subplots

from app import app 

#Variable con la ruta para salvar los querys
DATASET_DIRECTORY = "./datasets/"

#Lee el archivo de configuracion
configuracion = configparser.ConfigParser()

#Listado de archivos LAS
files = fnmatch.filter(os.listdir(DATASET_DIRECTORY), '*.las')

file_name = ''

layout = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.Row([
                    dbc.Col([
                        html.Label(['Archivo LAS:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                            id='dpd-las-list',
                            options=[
                                {'label': i, 'value': i} for i in files
                            ],
                            clearable=False
                        ),
                    ], width={"size": 4, "offset": 1}),
                ]),
                html.Br(),
           ], style={"background-color": "#F9FCFC"},),
        ], width={"size": 4}),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dac.Box([
                    dac.BoxHeader(
                        collapsible = False,
                        closable = False,
                        title="Marcadores Estratgráficos"
                    ),
                    dac.BoxBody([
                        dbc.Spinner(
                            dcc.Graph(id='cht-curve-chart'),
                        ),
                    ]),	
                ],
                color='primary',
                solid_header=True,
                elevation=4,
                width=12
            ),
        ], width=11),
    ]),
])

@app.callback(
    Output('cht-curve-chart','figure'),
    [Input("dpd-las-list", "value")])
def update_curve_chart(file_name):

    fig = {}
    if file_name:
        las = lasio.LASFile(DATASET_DIRECTORY+file_name)
        df = las.df()
        df.reset_index(inplace=True)
        df.rename(columns={'DEPT':'DEPTH'}, inplace=True)
        num_columns = len(df.columns)-1
        cols = 1
        columns_list = df.columns

        fig = make_subplots(rows=1, cols=num_columns, subplot_titles=columns_list[1:], shared_yaxes=True)

        for columna in columns_list[1:]:
            fig.add_trace(
                go.Scatter(x=df[columna], y=df["DEPTH"],name=columna),
                row=1, col=cols
            )
            cols = cols+1

        fig.update_layout(height=800, width=1400, title_text="Curvas del archivo: "+file_name)       
        fig.layout.plot_bgcolor='rgba(0,0,0,0)'
        fig.update_xaxes(showline=True,showgrid=True, gridwidth=1, gridcolor='Black', linewidth=1, linecolor='black', mirror=True)
        fig.update_yaxes(showline=True,showgrid=True, gridwidth=1, gridcolor='Black', linewidth=1, linecolor='black', mirror=True)
    return fig
