import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Row import Row
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash_table.Format import Format, Symbol
import dash_admin_components as dac
import dash_daq as daq
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash_table
import sqlite3
import configparser
import sys
import os.path
import os
from os import listdir
from os.path import isfile, join
import stumpy
import numpy as np
import numpy.testing as npt
import pandas as pd
from datetime import datetime, tzinfo, timezone, timedelta, date
from collections import OrderedDict
import base64
import json
import os
import datetime


from app import app
from library import update_columns_list, create_chart, create_chart_single, search_unit

#Lee el archivo de configuracion
configuracion = configparser.ConfigParser()

#Variable con la ruta para salvar los querys
QUERY_DIRECTORY = "./querys"
TEMPLATE_DIRECTORY = "./template/"

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

#Listado de unidades por variables
query = "SELECT * FROM UNIDADES"
unidades =pd.read_sql(query, con)

con.close()


#Listado de query
pathway = './querys'
files = [f for f in listdir(pathway) if isfile(join(pathway, f))]

file_name = ''

layout = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.Row([
                    dbc.Col([
                        html.Label(['Consulta:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                            id='dpd-query-lista',
                            options=[
                                {'label': i, 'value': i} for i in files
                            ],
                            clearable=False
                        ),
                    ], width={"size": 3, "offset": 1}),
                    dbc.Col([
                        html.Label(['Pozo:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                            id='dpd-well-list',
                            options=[{'label': i, 'value': i} for i in well_list],
                            clearable=False,
                        ),
                    ], width={"size": 2, "offset": 1}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button(html.Span(["historico", html.I(className="fas fa-chart-line-down ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                         id="btn_show_history", color="primary", className="mr-3"),
                    ], width={"size": 1, "offset": 0}),
                ]),
                html.Br(),
            ], style={"background-color": "#F9FCFC"},),
        ], width={"size": 6, "offset": 0}),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    dac.Box([
                            dac.BoxHeader(
                                collapsible = False,
                                closable = False,
                                title="Historico"
                            ),
                            dac.BoxBody([
                                dcc.Loading(
                                    dcc.Graph(id='cht-history-chart'),
                                ),
                            ]),	
                        ],
                        color='primary',
                        solid_header=True,
                        elevation=4,
                        width=12
                    ),
                ], width={"size": 12, "offset": 0}),
            ]),
        ], width=9),
        dbc.Col([
            dbc.Col([
                dac.Box([
                        dac.BoxHeader(
                            collapsible = False,
                            closable = False,
                            title="Parámetros"
                        ),
                        dac.BoxBody([
                            dcc.Checklist(
                                id="cb_clear_cero_data",
                                options=[{"label": "  Limpiar valores Ceros", "value": "YES"}],
                                value=[],
                                labelStyle={"display": "inline-block"},
                            ),
                            html.Br(),
                            html.Label(['Variable:'],style={'font-weight': 'bold', "text-align": "left"}),
                            dcc.Dropdown(
                                id='dpd-study-variable',
                                clearable=False,
                                multi=False
                            ),
                            html.Br(),
                            html.Label(['Patrón:'],style={'font-weight': 'bold', "text-align": "left"}),
                            dcc.Loading(
                                dcc.Graph(id='cht-pattern-chart', style={"height": 450},),
                            ),
                            html.Label(['Minimo:'],style={'font-weight': 'bold', "text-align": "left"}),
                            dbc.Input(id="inp-min-val", type="number", step=1, style={'backgroundColor':'white'}),
                            html.Label(['Maximo:'],style={'font-weight': 'bold', "text-align": "left"}),
                            dbc.Input(id="inp-max-val", type="number", step=1, style={'backgroundColor':'white'}),
                            html.Br(),
                            dbc.Button(html.Span(["mostrar", html.I(className="fas fa-chart-line-down ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                            id="btn_show_pattern", color="primary", className="mr-3"),
                            html.Br(),
                            dbc.Button(html.Span(["Identificar", html.I(className="fas fa-chart-line-down ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                            id="btn_find_pattern", color="primary", className="mr-3"),
                        ]),	
                    ],
                    color='primary',
                    solid_header=True,
                    elevation=4,
                    width=12,
                    style={"background-color": "#F9FCFC"},
                ),
            ]),
        ], width=3),
    ]),
])

@app.callback(
    Output('dpd-study-variable','options'),
    Input('dpd-query-lista', 'value'))
def update_column_list(file_name):

    columns = [{'label': i, 'value': i} for i in []]
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'dpd-query-lista' in changed_id:
        columns = update_columns_list(archivo, file_name, None)

    return columns

@app.callback(
    Output('cht-history-chart','figure'),
    [Input("btn_show_history", "n_clicks"),
     Input("btn_find_pattern", "n_clicks"),
     Input('dpd-query-lista', 'value'), 
     Input('dpd-well-list', 'value'),
     Input('dpd-study-variable', 'value'),
     Input('cb_clear_cero_data','value'),
     Input('inp-min-val','value'),
     Input('inp-max-val','value'),])
def update_history_chart(n_clicks, n_clicks2, file_name, well_name, column_var, clear_data, min_val, max_val):

    fig = {}
    color_line = dict(hex='#0bfc03')
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

    if 'btn_show_history' in changed_id or 'btn_find_pattern' in changed_id:
        if column_var:
            T_df = pd.DataFrame()
            T_df2 = pd.DataFrame()
            Q_df = pd.DataFrame()
            query= ''
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            con = sqlite3.connect(archivo)

            if file_name is not None:
                with open(os.path.join(QUERY_DIRECTORY, file_name)) as f:
                    contenido = f.readlines()
                if contenido is not None:
                    query = ''
                    for linea in contenido:
                        query +=  linea 

                    query1 = query + ' ORDER BY FECHA'

                    T_df =pd.read_sql(query1, con)

                    if well_name:
                        T_df = T_df[T_df['NOMBRE']==well_name]
                                          
                    if clear_data:
                        T_df = T_df[(T_df!=0)]

                    T_df['indice'] = np.arange(len(T_df))

                    if column_var:

                        #Valida que la columna seleccionada este en el dataframe
                        if column_var in T_df:
                            var_name, var_color = search_unit(unidades, column_var)

                            if var_color:
                                color_axis_y1 = dict(hex=var_color)
                                    
                            fig.add_trace(
                                go.Scatter(x=T_df['indice'],
                                    y=T_df[column_var],
                                    name=var_name,
                                    connectgaps=True,
                                    mode='lines',
                                    line_color=color_axis_y1["hex"],
                                    yaxis= 'y1'                             
                                ),
                            )
                        i=+1
                    if 'btn_find_pattern' in changed_id:
                        Q_df= T_df[(T_df['indice'] >= min_val) & (T_df['indice'] <= max_val)]

                        if clear_data:
                            Q_df = Q_df[(Q_df!=0)]

                        print("Longitud Q_df:", len(Q_df))
                        print("Longitud T_df:", len(T_df))

                        if len(Q_df)>0:
                            distance_profile = stumpy.core.mass(Q_df[column_var], T_df[column_var])

                            k = 16
                            idxs = np.argpartition(distance_profile, k)[:k]
                            idxs = idxs[np.argsort(distance_profile[idxs])]

                            for idx in idxs:
                                T_df2['indice'] = range(idx, idx+len(Q_df))
                                T_df2['valor'] = T_df[column_var].values[idx:idx+len(Q_df)]
                                fig.add_trace(
                                    go.Scatter(x=T_df2['indice'],
                                        y= T_df2['valor'],
                                        mode='lines',
                                        line_color=color_line["hex"],
                                        yaxis= 'y2',                               
                                    ),
                                )

                    fig.update_xaxes(title_text="FECHA",showline=True, linewidth=2, linecolor='black', showgrid=False,)
                    fig.update_yaxes(showline=True, linewidth=2, linecolor='black', showgrid=False,)
                    fig.update_layout(
                        autosize=False,
                        hovermode='x unified',
                        height=700,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgb(240, 240, 240)',
                        margin=dict(
                            l=50,
                            r=50,
                            b=100,
                            t=100,
                            pad=4,
                        ),
                        showlegend=False,
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        ),
                        )
                    fig.update_xaxes(
                    rangeslider_visible=True,
                        rangeselector=dict(
                            buttons=list([
                            dict(count=1, label="1m", step="month", stepmode="backward"),
                            dict(count=6, label="6m", step="month", stepmode="backward"),
                            dict(count=1, label="YTD", step="year", stepmode="todate"),
                            dict(count=1, label="1y", step="year", stepmode="backward"),
                            dict(step="all")
                            ])
                        )
                    )

            con.close()
    return fig

@app.callback(
    Output('cht-pattern-chart','figure'),
    [Input("btn_show_pattern", "n_clicks"),
     Input('dpd-query-lista', 'value'), 
     Input('dpd-well-list', 'value'),
     Input('dpd-study-variable', 'value'),
     Input('cb_clear_cero_data','value'),
     Input('inp-min-val','value'),
     Input('inp-max-val','value'),])
def update_pattern_chart(n_clicks, file_name, well_name, column_var, clear_data, min_val, max_val):

    fig = {}
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'btn_show_pattern' in changed_id:
        if column_var:
            fig = create_chart_single(archivo, unidades, file_name, well_name, column_var, clear_data, min_val, max_val)
    
    return fig

