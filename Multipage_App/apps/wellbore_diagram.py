import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Row import Row
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash_html_components.Br import Br
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

#Cargando imagen del wellbore diagram
img = io.imread('./pictures/wellbore.png')



layout = html.Div([
    dbc.Row([
        dbc.Col([
            html.Label(['Pozo:'],style={'font-weight': 'bold', "text-align": "left"}),
            dcc.Dropdown(
                id='dpd-well-list',
                options=[{'label': i, 'value': i} for i in well_list],
                clearable=False,
                multi=False
            ),
        ], width=4),
        dbc.Col([
            html.Br(),
            dbc.Button("Mostrar Gráficos", id="btn_show_chart", color="success", className="mr-3"),
        ], width=1.5),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.Label(['Esquematico'],style={'font-weight': 'bold', "text-align": "left"})),
                dbc.CardBody([
                    dbc.Spinner(
                        dcc.Graph(id='cht-wellbore-chart',style={"height": 400, "width":300}),
                    ),
                ])
            ],style={"height": "75rem"},),
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.Label(['Datos'],style={'font-weight': 'bold', "text-align": "left"})),
                dbc.CardBody([
                    dbc.Spinner(
                        dash_table.DataTable(id="dt-wellbore-detail", 
                        style_as_list_view=True,
                        style_cell={'padding': '5px'},
                        style_header={
                            'backgroundColor': 'blue',
                            'fontWeight': 'bold',
                            'color': 'white'
                        },
                        columns=[
                                {'id': 'DESCRIPCION', 'name': 'DESCRIPCION'},
                                {'id': 'ID', 'name': 'ID'},
                                {'id': 'OD', 'name': 'OD'},
                                {'id': 'MD', 'name': 'MD'},
                                {'id': 'LONGITUD', 'name': 'LONGITUD'},
                            ],
                        dropdown = {
                            'NOMBRE': {
                                'options': [
                                    {'label': i, 'value': i}
                                    for i in  well_list
                                ]
                            },
                            'TIPO': {    
                                'options': [
                                    {'label': 'Arbol Navidad', 'value': 'XMAST'},
                                    {'label': 'Valvula Seguridad', 'value': 'SAFEV'},
                                    {'label': 'Tubbing', 'value': 'TUBIN'},
                                    {'label': 'Casing 13 3/8', 'value': 'CASIN13'},
                                    {'label': 'Casing 12', 'value': 'CASIN12'},
                                    {'label': 'Cementacion', 'value': 'CEMEN'},
                                    {'label': 'Perforaciones', 'value': 'PERF'},
                                ],
                            }
                        },
                        page_action="native",
                        page_current= 0,
                        page_size= 10,),
                    ),
                ])
            ]),
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.Label(['Survey'],style={'font-weight': 'bold', "text-align": "left"})),
                dbc.CardBody([
                    dbc.Spinner(
                        dcc.Graph(id='cht-well-survey'),
                    ),
                ])
            ]),
        ], width=5),
    ]),
])

@app.callback(
    [Output('cht-well-survey','figure'),
    Output('cht-wellbore-chart','figure'),
    Output("dt-wellbore-detail", "data")],
    [Input("btn_show_chart", "n_clicks"),
     Input('dpd-well-list', 'value'),])
def update_survey_chart(n_clicks, well_name):
    fig1 = {}
    fig2 = {}
    wellbore_table = pd.DataFrame()
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'btn_show_chart' in changed_id:
        if well_name is not None:
            data_results= wells_surveys[wells_surveys['NOMBRE']==well_name]
            well = wp.load(data_results)     # LOAD WELL
            fig1 = well.plot(style={'size': 5})
            fig1.update_layout(width=580, height=600)

            fig2 = px.imshow(img)
            fig2.update_xaxes(showticklabels=False)
            fig2.update_yaxes(showticklabels=False)
            fig2.update_layout(width=300, height=650, margin=dict(l=0, r=0, b=0, t=0),paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)')

            #Estos anotations saldran de la tabla wellbore_detail 
            #Seran cargados como un ciclo


            #filtra el dataframe con el pozo
            wellbore_table = wellbore_detail[wellbore_detail['NOMBRE']==well_name]
            wellbore_table =wellbore_table.drop(['NOMBRE'], axis=1)
            for i in wellbore_table.index: 
                fig2.add_annotation(
                    x=300,
                    y=Decimal(wellbore_table["MD"][i])/10,
                    text=wellbore_table["DESCRIPCION"][i],
                    align="left",
                    #xref="paper",
                    #yref="paper",
                    xref="x",
                    yref="y",
                    showarrow=False,
                    font_size=10, font_color='blue')

    data = wellbore_table.to_dict('records')
    return fig1, fig2, data