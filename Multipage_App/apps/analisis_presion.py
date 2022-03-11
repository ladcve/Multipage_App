import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Row import Row
import dash_core_components as dcc
import dash_html_components as html
from plotly.subplots import make_subplots
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
from glob import glob
import os

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

layout = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.Row([
                    dbc.Col([
                        html.Label(['Pozo:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                            id='dpd-well-list-press',
                            options=[{'label': i, 'value': i} for i in well_list],
                            clearable=False,
                            multi=False
                        ),
                    ], width={"size": 4, "offset": 1}),
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
                        title="Listado Imagenes"
                    ),
                    dac.BoxBody([
                        dcc.RadioItems(id = "rb_file_list", style={"padding": "15px", "font-size": 18},)
                    ]),	
                ],
                color='primary',
                solid_header=True,
                elevation=4,
                width=12
            ),
        ], width=3),
        dbc.Col([
            dac.Box([
                    dac.BoxHeader(
                        collapsible = False,
                        closable = False,
                        title="Esquematico"
                    ),
                    dac.BoxBody([
                        dcc.Loading(
                            dcc.Graph(id='cht-analisis-presion'),
                        ),
                    ]),	
                ],
                color='primary',
                solid_header=True,
                elevation=4,
                width=12
            ),
        ], width=9),
    ]),
    dbc.Row([
        dac.Box([
                dac.BoxHeader(
                    collapsible = False,
                    closable = False,
                    title="Resumen PTA"
                ),
                dac.BoxBody([
                    dash_table.DataTable(id="dt_resumen_pta", 
                        style_as_list_view=True,
                        style_header={
                            'backgroundColor': 'blue',
                            'fontWeight': 'bold',
                            'color': 'white'
                        },
                        sort_action="native",
                        sort_mode="multi",
                        row_selectable="single",
                        row_deletable=False,
                        page_current= 0,
                        page_size= 10,
                        style_table={'height': '500px', 'overflowY': 'auto'},
                        style_cell={'textAlign': 'left', 'minWidth': '100px', 'width': '200px', 'maxWidth': '300px','font_size':'20px'},
                    )
                ]),	
            ],
            color='primary',
            solid_header=True,
            elevation=4,
            width=12
        ),
    ]),
])

@app.callback(
   Output('cht-analisis-presion','figure'),
    Input('rb_file_list', 'value'))
def update_img(file):
    fig = {}
    if file:
        img = io.imread(file)
        fig = px.imshow(img, aspect='auto')
        fig.update_layout(coloraxis_showscale=False,autosize=False, width=1200, height =500,modebar_orientation="v",
            margin=go.layout.Margin(
            l=0,
            r=0,
            b=0,
            t=0
        ))
        fig.update_xaxes(showticklabels=False)
        fig.update_yaxes(showticklabels=False)

    return fig

@app.callback(
   [Output('rb_file_list','options'),
   Output("dt_resumen_pta", "data"), Output("dt_resumen_pta", "columns")],
    Input('dpd-well-list-press', 'value'))
def update_file_list(well_name):

    df= pd.DataFrame()
    img_list = []

    if well_name is not None:
            
        #Lee la lista de archivos que comiencen por el nombre del pozo
        path = './pictures/'
        img_list = list(glob(os.path.join(path, well_name+"*analisis-presion.png")))

        #Listado de pozos activos
        con = sqlite3.connect(archivo)
        query = "SELECT * FROM RESUMEN_PTA WHERE NOMBRE='"+well_name+"'"
        df =pd.read_sql(query, con)
        con.close()

    columns = [{'name': i, 'id': i, "deletable": True} for i in df.columns]
    data = df.to_dict('records')

    return [{'label': x, 'value' : x } for x in img_list], data, columns