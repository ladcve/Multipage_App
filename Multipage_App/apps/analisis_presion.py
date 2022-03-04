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


#Define las columans de la tabla y su formato

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
                    dbc.Col([
                        html.Br(),
                        dbc.Button(html.Span(["mostrar ", html.I(className="fas fa-chart-bar ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                        id="btn_show_press_img", color="success", className="mr-3"),
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
                            dcc.Graph(id='cht-analisis-presion'),
                        ),
                    ]),	
                ],
                color='primary',
                solid_header=True,
                elevation=4,
                width=12
            ),
        ], width=12),
    ]),
])

@app.callback(
    Output('cht-analisis-presion','figure'),
    [Input("btn_show_press_img", "n_clicks"),
     Input('dpd-well-list-press', 'value'),])
def update_survey_chart(n_clicks, well_name):
    fig = {}
    wellbore_table = pd.DataFrame()
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    
    if 'btn_show_press_img' in changed_id:
        if well_name is not None:
            
            #Lee la lista de archivos que comiencen por el nombre del pozo
            path = './pictures/'
            img_list = list(glob(os.path.join(path, well_name+"*analisis-presion.png")))
            if img_list:
                chart_no=1
                fig = make_subplots(rows=1, 
                    horizontal_spacing=0.01, 
                    shared_yaxes=True,
                    cols=len(img_list))
                img_width = 9000
                img_height = 800
                scale_factor = 18
                for imagen in img_list:
                    img = io.imread(imagen)
                    fig.add_trace(go.Image(z=img,dx=10,dy=10), 1, chart_no)
                    fig.update_layout(coloraxis_showscale=False)
                    fig.update_xaxes(showticklabels=False)
                    fig.update_yaxes(showticklabels=False)
                    chart_no=chart_no+1

            
    #data = wellbore_table.to_dict('records')
    return fig