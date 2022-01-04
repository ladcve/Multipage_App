import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Row import Row
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ALL, MATCH
import dash_admin_components as dac
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
#las = lasio.LASFile(DATASET_DIRECTORY+"Perla-1X.LAS")
#curves_lits = []
#for curve in las.curves[1:]:
#    curves_lits.append(curve.mnemonic)

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
                                #options=[{'label': i, 'value': i} for i in well_list],
                                clearable=False,
                                multi = True,
                            ),
                        ], width={"size": 6, "offset": 1}),
                        dbc.Col([
                            dbc.Button(html.Span(["Mostrar ", html.I(className="fas fa-columns ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                             id="btn_show_section", color="success", className="mr-3"),
                        ]),
                    ]),
                ])
           ]),
        ], width={"size": 4}),
        html.Br(),
        dbc.Col([
            dbc.Card([
                dbc.Col([
                    dbc.CardHeader(html.Label(['Curvas'],style={'font-weight': 'bold', "text-align": "left"})),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Label(['seleccion de Curvas:'],style={'font-weight': 'bold', "text-align": "left"}),
                                dcc.Dropdown(
                                    id='dpd-curve-selection',
                                    #options=[{'label': i, 'value': i} for i in curves_lits],
                                    clearable=False,
                                    multi = True,
                                ),
                            ], width={"size": 5, "offset": 0}),
                            dbc.Col([
                                html.Label(['Tope:'],style={'font-weight': 'bold', "text-align": "left"}),
                                dbc.Input(id="inp-top-depht", placeholder="Type something...", type="text", style={'backgroundColor':'white'}),
                                html.Br(),
                                html.Label(['Base:'],style={'font-weight': 'bold', "text-align": "left"}),
                                dbc.Input(id="inp-botton-depht", placeholder="Type something...", type="text", style={'backgroundColor':'white'}),
                            ], width={"size": 3, "offset": 1}),
                            dbc.Col([
                                dcc.Checklist(
                                    id="cb_show_markers",
                                    options=[{"label": "  Mostrar marcadores", "value": "YES"}],
                                    value=[],
                                    labelStyle={"display": "inline-block"},
                                ),
                            ]),
                        ]),
                    ])
                ]),
            ]),
            
        ], width={"size": 6, "offset": 0}),
    ]),
    html.Br(),
    dac.Box([
            dac.BoxHeader(
                collapsible = False,
                closable = False,
                title="Cross Section"
            ),
            dac.BoxBody([
                dbc.Spinner(
                    html.Div(content),
                ),
            ]),	
        ],
        color='primary',
        solid_header=True,
        elevation=4,
        width=12
    ),
])


def create_cross_section(well_name, curve_list, show_marker):
    fig = {}
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'btn_show_section' in changed_id:
        if curve_list and well_name:
            las = lasio.LASFile(DATASET_DIRECTORY+well_name+'.las')
            df = las.df()
            df.reset_index(inplace=True)
            df.rename(columns={'DEPT':'DEPTH'}, inplace=True)
            cols = 1

            fig = make_subplots(rows=1, cols=len(curve_list), shared_yaxes=True )

            for curve in curve_list:
                fig.add_trace(
                    go.Scatter(x=df[curve], y=df["DEPTH"]),
                    row=1, col=cols
                )
                fig.update_xaxes(title_text=curve,  side= 'top', row=1, col=cols)

                cols = cols+1

            fig.update_layout(height=810, width=350,
                title={
                    'text': "Pozo: "+well_name,
                    'y':0.99,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'}
                )       
            fig.layout.plot_bgcolor='rgba(0,0,0,0)'
            fig.update_xaxes(showline=True,showgrid=True, gridwidth=1, gridcolor='Black', linewidth=1, linecolor='black', mirror=True)
            fig.update_yaxes(showline=True,showgrid=True, gridwidth=1, gridcolor='Black', linewidth=1, linecolor='black', mirror=True, autorange="reversed")
            fig.update_layout(showlegend=False)

            if show_marker:
                fig.add_annotation(
                    x=0.5
                    , y=1500
                    , text=f'Formacion prueba'
                    , yanchor='bottom'
                    , showarrow=False
                    , arrowhead=1
                    , arrowsize=1
                    , arrowwidth=2
                    , arrowcolor="#636363"
                    , ax=-20
                    , ay=-30
                    , font=dict(size=12, color="orange", family="Sans Serif")
                    , align="left"
                    ,)
                # add vertical lines
                fig.update_layout(shapes=
                    [dict(type= 'line',
                            xref= 'paper', x0= 0, x1= 1,
                            yref= 'y', y0=1500, y1=1500,
                            line=dict(color="MediumPurple",
                                    width=3,
                                    dash="dot")
                            ),
                    ])

    return fig

@app.callback(
    Output("cont-grafico", "children"),
    [
        Input("btn_show_section", "n_clicks"),
        Input("dpd-wells-lists", "value"),
        Input('dpd-curve-selection', 'value'), 
        Input('cb_show_markers', 'value'),
    ],
    [State("cont-grafico", "children")],
)
def display_cross_section(n_clicks, well_list, curve_list, show_marker, children):
    query = ''
    input_id = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
    if 'btn_show_section' in input_id:
        for well in well_list:
            new_element = html.Div(
                    style={
                    "width": "  19%",
                    "display": "inline-block",
                    "outline": "thin lightgrey solid",
                    "padding": 5,
                },
                children=[
                    dcc.Graph(
                        id={"type": "dynamic-output", "index": n_clicks},
                        figure=create_cross_section(well, curve_list, show_marker ),
                    ),
                ]
            )
            children.append(new_element)
    return children