import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Row import Row
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ALL, MATCH
from dash_html_components.Br import Br
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash_table
import configparser
import sqlite3
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

#Lee el archivo de configuracion
configuracion = configparser.ConfigParser()

#Variable con la ruta para salvar los querys
DATASET_DIRECTORY = "./datasets/"

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

con.close()

#Obtener nombre de las curvas de un archivo las
las = lasio.LASFile(DATASET_DIRECTORY+"Perla-1X.LAS")
curves_lits = []
for curve in las.curves[1:]:
    curves_lits.append(curve.mnemonic)

#Lee el archivo de configuracion
configuracion = configparser.ConfigParser()

file_name = ''

# padding for the page content
content = html.Div(id="cont-grafico", children=[])

layout = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.Label(['Pozos:'],style={'font-weight': 'bold', "text-align": "left"})),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dcc.Dropdown(
                                id='dpd-wells-lists',
                                options=[{'label': i, 'value': i} for i in well_list],
                                clearable=False,
                                multi = True,
                            ),
                        ], width={"size": 6, "offset": 1}),
                        dbc.Col([
                            dbc.Button("Mostrar Seccion", id="btn_show_section", color="success", className="mr-3"),
                        ]),
                    ]),
                ])
           ]),
        ], width={"size": 4}),
        html.Br(),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.Label(['Curvas'],style={'font-weight': 'bold', "text-align": "left"})),
                dbc.CardBody([
                    html.Label(['seleccion de Curvas:'],style={'font-weight': 'bold', "text-align": "left"}),
                    dcc.Dropdown(
                        id='dpd-curve-selection',
                        options=[{'label': i, 'value': i} for i in curves_lits],
                        clearable=False,
                        multi = True,
                    ),
                ])
            ]),
        ], width=3),
    ]),
    html.Br(),
    html.Div(content),
])


def create_cross_section(well_name, curve_list):
    fig = {}
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'btn_show_section' in changed_id:
        if curve_list and well_name:
            las = lasio.LASFile(DATASET_DIRECTORY+well_name+'.las')
            df = las.df()
            df.reset_index(inplace=True)
            df.rename(columns={'DEPT':'DEPTH'}, inplace=True)
            cols = 1

            fig = make_subplots(rows=1, cols=2, shared_yaxes=True, horizontal_spacing=0  )

            for curve in curve_list:
                fig.add_trace(
                    go.Scatter(x=df[curve], y=df["DEPTH"]),
                    row=1, col=cols
                )
                fig.update_layout(showlegend=False, xaxis={'side': 'top'},xaxis_title=curve,)
                cols = cols+1

            fig.update_layout(height=800, width=350, title_text="Pozo: "+well_name)       
            fig.layout.plot_bgcolor='rgba(0,0,0,0)'
            fig.update_xaxes(showline=True,showgrid=True, gridwidth=1, gridcolor='Black', linewidth=1, linecolor='black', mirror=True)
            fig.update_yaxes(showline=True,showgrid=True, gridwidth=1, gridcolor='Black', linewidth=1, linecolor='black', mirror=True)
            
    return fig

@app.callback(
    Output("cont-grafico", "children"),
    [
        Input("btn_show_section", "n_clicks"),
        Input("dpd-wells-lists", "value"),
        Input('dpd-curve-selection', 'value')
    ],
    [State("cont-grafico", "children")],
)
def display_cross_section(n_clicks, well_list, curve_list, children):
    query = ''
    input_id = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
    if 'btn_show_section' in input_id:
        for well in well_list:
            new_element = html.Div(
                    style={
                    "width": "  20%",
                    "display": "inline-block",
                    "outline": "thin lightgrey solid",
                    "padding": 5,
                },
                children=[
                    dcc.Graph(
                        id={"type": "dynamic-output", "index": n_clicks},
                        figure=create_cross_section(well, curve_list ),
                    ),
                ]
            )
            children.append(new_element)
    return children