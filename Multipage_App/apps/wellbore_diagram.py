import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Row import Row
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash_table.Format import Format, Symbol
import dash_admin_components as dac
import plotly.express as px
import plotly.graph_objects as go
import well_profile as wp
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
from skimage import io
from decimal import Decimal

from app import app


#Variable con la ruta para salvar los querys
LOAD_DIRECTORY = "./datasets/"
IMAGEN_DIRECTORY = "./picture/"

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

#Cargar todos los survey de los pozos
query = "SELECT * FROM SURVEY"
wells_surveys =pd.read_sql(query, con)

#Cargar el detalle de la completacion
query = "SELECT * FROM WELLBORE"
wellbore_detail =pd.read_sql(query, con)


#Define las columans de la tabla y su formato

layout = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.Row([
                    dbc.Col([
                        html.Label(['Pozo:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                            id='dpd-well-list',
                            options=[{'label': i, 'value': i} for i in well_list],
                            clearable=False,
                            multi=False
                        ),
                    ], width={"size": 4, "offset": 1}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button(html.Span(["mostrar ", html.I(className="fas fa-chart-bar ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                        id="btn_show_chart", color="success", className="mr-3"),
                    ], width={"size": 2, "offset": 0}),
                ]),
                html.Br(),
            ], style={"background-color": "#F9FCFC"},),
        ], width={"size": 4, "offset": 0}),
        dbc.Col([
            dbc.Card([
                dbc.Row([
                    dbc.Col([
                        html.Label(['Pozo:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                            id='dpd-well-list-survey',
                            options=[{'label': i, 'value': i} for i in well_list],
                            clearable=False,
                            multi=True
                        ),
                    ], width={"size": 6, "offset": 1}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button(html.Span(["mostrar ", html.I(className="fas fa-chart-bar ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                        id="btn_show_survey", color="success", className="mr-3"),
                    ], width={"size": 2, "offset": 0}),
                ]),
                html.Br(),
            ], style={"background-color": "#F9FCFC"},),
        ], width={"size": 4, "offset": 0}),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dac.Box([
                    dac.BoxHeader(
                        collapsible = False,
                        closable = False,
                        title="Esquematico"
                    ),
                    dac.BoxBody([
                        dcc.Loading(
                            dcc.Graph(id='cht-wellbore-chart',style={"height": 950, "width":300}),
                        ),
                    ]),	
                ],
                color='primary',
                solid_header=True,
                elevation=4,
                width=12
            ),
        ], width=5),
        dbc.Col([
            dac.Box([
                    dac.BoxHeader(
                        collapsible = False,
                        closable = False,
                        title="Survey"
                    ),
                    dac.BoxBody([
                        dcc.Loading(
                            dcc.Graph(id='cht-well-survey',style={"height": 950, "width":300}),
                        ),
                    ]),	
                ],
                color='primary',
                solid_header=True,
                elevation=4,
                width=12
            ),
        ], width=7),
    ]),
    dbc.Modal(
        [
            dbc.ModalHeader("error"),
        ],
        id="modal_error_wellbore",
        is_open=False,
    ),
    dbc.Modal(
        [
            dbc.ModalHeader("error"),
        ],
        id="modal_error_view_survey",
        is_open=False,
    ),
])

@app.callback(
    [Output('cht-wellbore-chart','figure'), Output('modal_error_wellbore', 'is_open')],
    [Input("btn_show_chart", "n_clicks"),
     Input('dpd-well-list', 'value')],
     State('modal_error_wellbore','is_open'))
def update_survey_chart(n_clicks,well_name, is_open):
    fig = {}
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    
    if 'btn_show_chart' in changed_id:
        if well_name:
            try:
                #Cargando imagen del wellbore diagram
                image_filename = './pictures/'+well_name+'.png'
                wellbore = base64.b64encode(open(image_filename, 'rb').read())

                #Mostrar imagen de la completacion del pozo
                img = io.imread(image_filename)
                fig = px.imshow(img, aspect='auto')
                fig.update_layout(coloraxis_showscale=False,autosize=False, width=700, height =950,modebar_orientation="v",
                    margin=go.layout.Margin(
                    l=0,
                    r=0,
                    b=0,
                    t=0
                ))
                fig.update_xaxes(showticklabels=False)
                fig.update_yaxes(showticklabels=False)

            except Exception  as e:
                    is_open = True
                    children = [dbc.ModalHeader("Error"),
                        dbc.ModalBody(
                            html.H6('Error: {}'.format(e), style={'textAlign': 'center', 'padding': 10}),
                        ),
                    ]
    return fig, is_open

@app.callback(
    [Output('cht-well-survey','figure'),  Output('modal_error_view_survey', 'is_open')],
    [Input("btn_show_survey", "n_clicks"),
     Input('dpd-well-list-survey', 'value')],
     State('modal_error_view_survey','is_open'))
def update_survey_chart(n_clicks, well_name_list, is_open):
    fig = {}
    well_list=[]
    wells_names=[]

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

    if 'btn_show_survey' in changed_id:
        if well_name_list:
            try:
                number = 1
                for well in well_name_list:
                    data_results= wells_surveys[wells_surveys['NOMBRE']==well]
                    if len(data_results)>0:
                        if number>1:
                            survey = wp.load(data_results)
                            well_list.append(survey)
                        else:
                            pozo = wp.load(data_results)
                        wells_names.append(well)
                        number += 1

                fig = pozo.plot(add_well=well_list, names=wells_names, style={'darkMode': True,'color': 'dls', 'size': 5})
                fig.update_layout(width=1100, height=950)

            except Exception  as e:
                    is_open = True
                    children = [dbc.ModalHeader("Error"),
                        dbc.ModalBody(
                            html.H6('Error: {}'.format(e), style={'textAlign': 'center', 'padding': 10}),
                        ),
                    ]
    #data = wellbore_table.to_dict('records')
    return fig,  is_open