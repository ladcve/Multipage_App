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
from library import find_file

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
query = "SELECT NOMBRE FROM ITEMS"
well_list =pd.read_sql(query, con)
well_list = well_list.sort_values('NOMBRE')['NOMBRE'].unique()

con.close()

#Obtener nombre de las curvas de un archivo las
las = lasio.LASFile(DATASET_DIRECTORY+"Perla-1X_part1.las")
general_curves_list = []
for curve in las.curves[1:]:
    general_curves_list.append(curve.mnemonic)

#Lee el archivo de configuracion
configuracion = configparser.ConfigParser()

file_name = ''

def search_list(list, element):
    for i in range(len(list)):
        if list[i] == element:
            return True
    return False

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
                            dbc.Button(html.Span(["Mostrar ", html.I(className="fas fa-columns ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                             id="btn_show_section", color="success", className="mr-3"),
                        ]),
                    ]),
                ])
           ], style={"background-color": "#F9FCFC"},),
        ], width={"size": 4}),
        html.Br(),
        dbc.Col([
            dbc.Card([
                dbc.Col([
                    dbc.CardHeader(html.Label(['Curvas'],style={'font-weight': 'bold', "text-align": "left"})),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Label(['Segmento:'],style={'font-weight': 'bold', "text-align": "left"}),
                                dcc.Dropdown(
                                    id='dpd-curve-segment',
                                    options=[
                                        {'label': '2950-7000', 'value': 'part1'},
                                        {'label': '7000-8700', 'value': 'part2'},
                                        {'label': '8700-9000', 'value': 'part3'},
                                        {'label': '9000-10350', 'value': 'part4'},
                                        {'label': '8800-10000', 'value': 'part5'},
                                    ],
                                    value='part1',
                                    clearable=False,
                                    multi=False,
                                ),
                            ], width={"size": 2, "offset": 0}),
                            dbc.Col([
                                html.Label(['seleccion de Curvas:'],style={'font-weight': 'bold', "text-align": "left"}),
                                dcc.Dropdown(
                                    id='dpd-curve-selection',
                                    #options=[{'label': i, 'value': i} for i in general_curves_list],
                                    clearable=False,
                                    multi = True,
                                ),
                            ], width={"size": 3, "offset": 0}),
                            dbc.Col([
                                dbc.Row([
                                    dbc.Col([
                                        html.Label(['Tope:'],style={'font-weight': 'bold', "text-align": "left"}),
                                        dbc.Input(id="inp-top-depht", placeholder="top depth", min=0, type="number", style={'backgroundColor':'white'}),
                                    ]),
                                    dbc.Col([
                                        html.Label(['Base:'],style={'font-weight': 'bold', "text-align": "left"}),
                                        dbc.Input(id="inp-botton-depht", placeholder="bottom depth", min=0, type="number", style={'backgroundColor':'white'}),
                                    ]),
                                ]),
                            ], width={"size": 2, "offset": 0}),
                            dbc.Col([
                                dcc.Checklist(
                                    id="cb_show_markers",
                                    options=[{"label": "  Mostrar marcadores", "value": "YES"}],
                                    value=[],
                                    labelStyle={"display": "inline-block"},
                                ),
                            ], width={"size": 2, "offset": 0}),
                        ]),
                    ])
                ]),
            ], style={"background-color": "#F9FCFC"},),
        ], width={"size": 8, "offset": 0}),
    ]),
    html.Br(),
    dac.Box([
            dac.BoxHeader(
                collapsible = False,
                closable = False,
                title="Cross Section"
            ),
            dac.BoxBody([
                dbc.Row([
                    dbc.Button(html.Span(["Borrar ", html.I(className="fas fa-trash-alt ml-1")],style={'font-size':'1.5em','text-align':'left'}),
                        id="btn_clear_section", color="danger", className="mr-3"),
                ]),
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


def create_cross_section(archivo, well_name, selected_curves, show_marker, segment, tope, base):
    fig = {}
    path = ''
    df = pd.DataFrame()
    curves_list_filter = []
    index = 0

    if selected_curves and well_name:
        #Listado de pozos activos
        con = sqlite3.connect(archivo)
        query = "SELECT * FROM MARCADORES"
        marcadores =pd.read_sql(query, con)

        path = DATASET_DIRECTORY+well_name+"_"+segment+".las"
        
        if os.path.exists(path):
            las = lasio.LASFile(path)
            df = las.df()

            curves_in_las = []
            for curve in las.curves[1:]:
                curves_in_las.append(curve.mnemonic)

            df.reset_index(inplace=True)
            df.rename(columns={'DEPT':'DEPTH'}, inplace=True)
            cols = 1

            fig = make_subplots(rows=1, cols=len(selected_curves), shared_yaxes=True )

            if tope is not None and base is not None:
                df = df[(df['DEPTH']>=tope) & (df['DEPTH']<=base)]

            for curve in curves_in_las:
                if search_list(selected_curves, curve):
                    curves_list_filter.append(curve)

            if len(curves_list_filter)>0:
                for curve in curves_list_filter:
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
                    marcadores = marcadores[(marcadores['MD']>=tope) & (marcadores['MD']<=base) & (marcadores['NOMBRE']==well_name) ]

                    for i, row in marcadores.iterrows():
                        fig.add_annotation(
                            x=0.5
                            , y=row['MD']
                            , text=row['FORMACION']
                            , yanchor='bottom'
                            , showarrow=False
                            , arrowhead=1
                            , arrowsize=1
                            , arrowwidth=2
                            , arrowcolor="#636363"
                            , ax=-20
                            , ay=-30
                            , font=dict(size=12, color="red", family="Sans Serif")
                            , align="left"
                            ,)
                        # add vertical lines
                        fig.add_shape(type="line",
                            xref= 'paper', 
                            yref= 'y',
                            x0=0, y0=row['MD'], x1=1, y1=row['MD'],
                            line=dict(color="DarkOrange",
                                            width=3,
                                            dash="dot")
                        )

    return fig

@app.callback(
    Output("cont-grafico", "children"),
    [
        Input("btn_show_section", "n_clicks"),
        Input("btn_clear_section", "n_clicks"),
        Input("dpd-wells-lists", "value"),
        Input('dpd-curve-selection', 'value'), 
        Input('cb_show_markers', 'value'),
        Input('dpd-curve-segment','value'),
        Input('inp-top-depht', 'value'),
        Input('inp-botton-depht', 'value'),
    ],
    [State("cont-grafico", "children")],
)
def display_cross_section(n_clicks, _, well_list, selected_curves, show_marker,segment, tope, base, children ):
    query = ''
    input_id = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
    if "btn_clear_section" in input_id:
        children = []
    if 'btn_show_section' in input_id:
        for well in well_list:
            path = DATASET_DIRECTORY+well+"_"+segment+".las"
            if os.path.exists(path):
                new_element = html.Div(
                        style={
                        "width": "  19%",
                        "display": "inline-block",
                        "outline": "thin lightgrey solid",
                        "padding": 5,
                    },
                    children=[
                        dbc.Row([
                            dcc.Graph(
                                id={"type": "dynamic-output", "index": n_clicks},
                                figure=create_cross_section(archivo, well, selected_curves, show_marker, segment, tope, base ),
                            ),
                        ]),
                    ]
                )
                children.append(new_element)
    return children


@app.callback(
    Output("dpd-curve-selection", "options"),
    Input("dpd-curve-segment", "value"),
)
def update_curve_lis(segment):
    options=[{'label': i, 'value': i} for i in []]
    path = DATASET_DIRECTORY+"Perla-1X_"+segment+".las"
    if os.path.exists(path):
        las = lasio.LASFile(path)
        curves_lits = []
        
        for curve in las.curves[1:]:
            curves_lits.append(curve.mnemonic)
            options=[{'label': i, 'value': i} for i in curves_lits]

    return options
