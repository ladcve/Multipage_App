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
from mbal import gascondensate

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


layout = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.Row([
                    dbc.Col([
                        html.Br(),
                        dbc.Button(html.Span(["Mostrar ", html.I(className="fas fa-map ml-1")],style={'font-size':'1.5em','text-align':'center'}), 
                        id="btn_show_balance", color="success", className="mr-3"),
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
                        dbc.Input(id="inp-ruta-balance", placeholder="Type something...", type="text", style={'backgroundColor':'white'}),
                    ], width={"size": 3, "offset": 1}),
                     dbc.Col([
                        html.Br(),
                        dcc.Upload(
                            dbc.Button(
                                html.Span(["Abrir ", html.I(className="fas fa-upload ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                                n_clicks=0, color="primary", className="mr-3"
                            ),
                            id='btn_open_balance',
                            multiple=False
                        ),
                    ], width={"size": 2, "offset": 0}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button(html.Span(["Grabar ", html.I(className="fas fa-save ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                            id="btn_save_balance", 
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
                        title="F vs Eg"
                    ),
                    dac.BoxBody([
                        dcc.Loading(
                            dcc.Graph(id='cht-chart-1', style={"width": "100%"}),
                        ),
                    ]),	
                ],
                color='primary',
                solid_header=True,
                elevation=4,
                width=12
            ),
        ], width=4),
        dbc.Col([
            dac.Box([
                    dac.BoxHeader(
                        collapsible = False,
                        closable = False,
                        title="p/z vs Gp"
                    ),
                    dac.BoxBody([
                        dcc.Loading(
                            dcc.Graph(id='cht-chart-2', style={"width": "100%"}),
                        ),
                    ]),	
                ],
                color='primary',
                solid_header=True,
                elevation=4,
                width=12
            ),
        ], width=4),
        dbc.Col([
            dac.Box([
                    dac.BoxHeader(
                        collapsible = False,
                        closable = False,
                        title="Párametros"
                    ),
                    dac.BoxBody([     
                        dbc.Row([
                            dbc.Col([
                            html.Label(['Compresibilidad de la formación'],style={'font-weight': 'bold', "text-align": "left"}),
                            ]),
                            dbc.Col([
                                dbc.Input(id="inp_cf", placeholder="Type something...", value=0, min=0, inputMode="numeric", type="number", style={'backgroundColor':'white'}),
                            ]),
                        ]),
                        html.Br(),
                        dbc.Row([
                            dbc.Col([  
                                html.Label(['Compresibilidad de fluidos: '],style={'font-weight': 'bold', "text-align": "left"}),
                            ]),
                            dbc.Col([
                                dbc.Input(id="inp_cw", placeholder="Type something...", value=0,min=0, type="number", style={'backgroundColor':'white'}),
                            ]),
                        ]),
                        html.Br(),
                        dbc.Row([
                            dbc.Col([

                                html.Label(['Dew-point: '],style={'font-weight': 'bold', "text-align": "left"}),
                            ]),
                            dbc.Col([
                                dbc.Input(id="inp_dp", placeholder="Type something...", value=0, min=0, type="number", style={'backgroundColor':'white'}),
                            ]),
                        ]),
                        html.Br(),
                        dbc.Row([
                            dbc.Col([
                                html.Label(['SWI: '],style={'font-weight': 'bold', "text-align": "left"}),
                            ]),
                            dbc.Col([
                                dbc.Input(id="inp_swi", placeholder="Type something...", value=0, min=0, type="number", style={'backgroundColor':'white'}),
                            ]),
                        ]),
                        dbc.Row([
                            html.Label(['Resultados Grafico 1: '],style={'font-weight': 'bold', "text-align": "left", "margin-left": "15px"}),
                            html.Label(html.Div(id="txt-chart1"),style={'font-weight': 'bold', 'color':'blue', "text-align": "left", "margin-left": "15px"}),
                        ]),
                        dbc.Row([
                            html.Label(['Resultados Grafico 2: '],style={'font-weight': 'bold', "text-align": "left", "margin-left": "15px"}),
                            html.Label(html.Div(id="txt-chart2"),style={'font-weight': 'bold', 'color':'blue', "text-align": "left", "margin-left": "15px"}),
                        ]),
                        dbc.Row([
                            html.Label(['Resultados Grafico 3: '],style={'font-weight': 'bold', "text-align": "left", "margin-left": "15px"}),
                            html.Label(html.Div(id="txt-chart3"),style={'font-weight': 'bold', 'color':'blue', "text-align": "left", "margin-left": "15px"}),
                        ]),
                        dbc.Row([
                            html.Label(['Resultados Grafico 4: '],style={'font-weight': 'bold', "text-align": "left", "margin-left": "15px"}),
                            html.Label(html.Div(id="txt-chart4"),style={'font-weight': 'bold', 'color':'blue', "text-align": "left", "margin-left": "15px"}),
                        ]),
                        dbc.Row([
                            html.Label(['Resultados Grafico 5: '],style={'font-weight': 'bold', "text-align": "left", "margin-left": "15px"}),
                            html.Label(html.Div(id="txt-chart5"),style={'font-weight': 'bold', 'color':'blue', "text-align": "left", "margin-left": "15px"}),
                        ]),
                    ]),	
                ],
                color='primary',
                solid_header=True,
                elevation=4,
                width=12,
                style={"background-color": "#F9FCFC"},
            ),
        ], width=4),
    ]),
    dbc.Row([
        dbc.Col([
            dac.Box([
                    dac.BoxHeader(
                        collapsible = False,
                        closable = False,
                        title="Diagnostico WaterDriver"
                    ),
                    dac.BoxBody([
                        dcc.Loading(
                            dcc.Graph(id='cht-chart-3', style={"width": "100%"}),
                        ),
                    ]),	
                ],
                color='primary',
                solid_header=True,
                elevation=4,
                width=12
            ),
        ], width=4),
        dbc.Col([
            dac.Box([
                    dac.BoxHeader(
                        collapsible = False,
                        closable = False,
                        title="F vs (Eg+Bgi*Efw)"
                    ),
                    dac.BoxBody([
                        dcc.Loading(
                            dcc.Graph(id='cht-chart-4', style={"width": "100%"}),
                        ),
                    ]),	
                ],
                color='primary',
                solid_header=True,
                elevation=4,
                width=12
            ),
        ], width=4),
        dbc.Col([
            dac.Box([
                    dac.BoxHeader(
                        collapsible = False,
                        closable = False,
                        title="((p/z)*1-Efw)) vs Gp"
                    ),
                    dac.BoxBody([
                        dcc.Loading(
                            dcc.Graph(id='cht-chart-5', style={"width": "100%"}),
                        ),
                    ]),	
                ],
                color='primary',
                solid_header=True,
                elevation=4,
                width=12
            ),
        ], width=4),
    ]),
    dbc.Modal(
        [
            dbc.ModalHeader("Plantilla Salvada"),
        ],
        id="modal_bal",
        is_open=False,
    ),
    dbc.Modal(
        [
            dbc.ModalHeader("error"),
        ],
        id="modal_error_bal",
        is_open=False,
    ),
])

@app.callback(
    [Output("cht-chart-1", "figure"),
    Output("cht-chart-2", "figure"),
    Output("cht-chart-3", "figure"),
    Output("cht-chart-4", "figure"),
    Output("cht-chart-5", "figure"),
    Output('txt-chart1','children'),
    Output('txt-chart2','children'),
    Output('txt-chart3','children'),
    Output('txt-chart4','children'),
    Output('txt-chart5','children'),
    Output("modal_error_bal", "is_open")],
    [Input("btn_show_balance", "n_clicks"),
    Input("inp_cf", "value"),
    Input("inp_cw", "value"),
    Input("inp_dp", "value"),
    Input("inp_swi", "value"),],
    [State('modal_error_bal','is_open')]
)
def run_balance(n_clicks, cf, cw, pdew, swi, is_open):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    mensaje = ''
    fig1={}
    fig2={}
    fig3={}
    fig4={}
    fig5={}
    txt_chart1=''
    txt_chart2=''
    txt_chart3=''
    txt_chart4=''
    txt_chart5=''
    if 'btn_show_balance' in changed_id:
        con = sqlite3.connect(archivo)
        query = 'SELECT * FROM PVT'
        pvt =pd.read_sql(query, con)
        con.close()

        # define variables
        press = pvt['P'].values
        Bg = pvt['Bg'].values * (1 / 1E+3) # convert to res ft3/scf
        Bo = pvt['Bo'].values 
        Np = pvt['Np'].values
        Gp = pvt['Gp'].values * 1E+9 # convert to scf
        Gi = np.zeros(len(pvt)) # zeros, no gas injection for cycling
        Rs = pvt['Rs'].values 
        Rv = pvt['Rv'].values * (1 / 1E+6) # convert to STB/MMSCF
        z = pvt['Z'].values * (1 / 1E+6) # gas compressibility factor

        # initialize with type of reservoir: gas-condensate
        type = gascondensate()

        # calculate MBAL parameters
        if  cf or cw or pdew or swi:
            if cf>=0 and cw>=0 and pdew>=0 and swi>=0:
                F, Btg, Efw, Eg = gascondensate.calculate_params(type, press, pdew, Bg, Bo, Np, Gp,Gi, cf, cw, swi, Rs, Rv)

                # plot MBAL
                fig1, fig2, fig3, fig4, fig5, txt_chart1, txt_chart2, txt_chart3, txt_chart4, txt_chart5 = gascondensate.plot(type, press, z, Gp, F, Btg, Efw, Eg, Rv)

    return fig1, fig2, fig3, fig4, fig5, txt_chart1, txt_chart2, txt_chart3, txt_chart4, txt_chart5, is_open

@app.callback(
    Output('modal_bal','is_open'),
    [Input('btn_save_balance', 'n_clicks'),
    Input("inp_cf", "value"),
    Input("inp_cw", "value"),
    Input("inp_dp", "value"),
    Input("inp_swi", "value"),
    Input('inp-ruta-balance', 'value'),
    State('modal_bal','is_open')]) 
def save_mbalance(n_clicks, inp_cf, inp_cw, inp_dp, inp_swi, file_name, is_open ):
    mensaje=''
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'btn_save_balance' in changed_id:
        if file_name:
            data = {}
            data['mbalance'] = []
            data['mbalance'].append({
                'inp_cf': inp_cf,
                'inp_cw': inp_cw,
                'inp_dp': inp_dp,
                'inp_swi': inp_swi,
                })
            with open(CHART_DIRECTORY+file_name, 'w') as file:
                json.dump(data, file, indent=4)
            is_open =True
    return is_open

@app.callback( [Output("inp_cf", "value"),
                Output("inp_cw", "value"),
                Output("inp_dp", "value"),
                Output("inp_swi", "value"),
                ],
              [Input('btn_open_balance', 'filename'),
              Input('btn_open_balance', 'contents')]
              )
def open_mbalance( list_of_names, list_of_contents):
    archivo = list_of_names
    inp_cf=0
    inp_cw=0
    inp_dp=0
    inp_swi=0

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'btn_open_balance' in changed_id:
        if list_of_names is not None:
            archivo = list_of_names
            with open(CHART_DIRECTORY+archivo) as file:
                data = json.load(file)
                for drop_values   in data['mbalance']:
                    inp_cf = drop_values['inp_cf']
                    inp_cw = drop_values['inp_cw']
                    inp_dp = drop_values['inp_dp']
                    inp_swi = drop_values['inp_swi']

    return inp_cf, inp_cw, inp_dp, inp_swi