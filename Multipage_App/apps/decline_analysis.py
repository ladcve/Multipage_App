import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Row import Row
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash_html_components.Br import Br
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
import numpy as np
import pandas as pd
from datetime import date
from collections import OrderedDict
import base64
import json
import os
import datetime
from scipy.optimize import curve_fit

from app import app 

#Lee el archivo de configuracion
configuracion = configparser.ConfigParser()

#Variable con la ruta para salvar los querys
QUERY_DIRECTORY = "./querys"
CHART_DIRECTORY = "./template/"

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

#Crea dataframe con datos de produccion
query = "SELECT NOMBRE, FECHA, TASA_GAS FROM CIERRE_DIARIO_POZO ORDER BY FECHA "
daily_prod =pd.read_sql(query, con)

con.close()

# Define las funciones de declinacion
def hyperbolic(t, qi, di, b):
  return qi / (np.abs((1 + b * di * t))**(1/b))

def exponential(t, qi, di):
    return qi*np.exp(-di*t)

def harmonic(t, qi, di):
    return qi/(1+di*t)

# function for hyperbolic cumulative production
def cumpro(q_forecast, qi, di, b):
    return (((qi**b) / ((1 - b) * di)) * ((qi ** (1 - b)) - (q_forecast ** (1 - b))))  

layout = html.Div([
    dbc.Row([
        dbc.Col([
            html.Label(['Pozo:'],style={'font-weight': 'bold', "text-align": "left"}),
            dcc.Dropdown(
                id='dpd-well-list',
                options=[{'label': i, 'value': i} for i in well_list],
                clearable=False,
            ),
        ], width={"size": 2, "offset": 0}),
        dbc.Col([
            html.Br(),
            dbc.Button("Mostrar Grafico", id="btn_show_data_prod", color="primary", className="mr-3"),
        ], width={"size": 1, "offset": 0}),
        dbc.Col([
            html.Br(),
            dbc.Button("Ejecutar Pronostico", id="btn_run_forecast", color="primary", className="mr-3"),
        ], width={"size": 1, "offset": 1}),
        dbc.Col([
            html.Br(),
            dbc.Button("Salvar Pronostico", id="btn_save_forecast", color="success", className="mr-3"),
        ], width={"size": 1, "offset": 1}),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.Label(['Curva de Declinación'],style={'font-weight': 'bold', "text-align": "left"})),
                        dbc.CardBody([
                            dbc.Spinner(
                                dcc.Graph(id='cht-decline-chart'),
                            ),
                        ])
                    ]),
                ], width={"size": 6, "offset": 0}),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.Label(['Curva de Acumulado'],style={'font-weight': 'bold', "text-align": "left"})),
                        dbc.CardBody([
                            dbc.Spinner(
                                dcc.Graph(id='cht-cumulative-chart'),
                            ),
                        ])
                    ]),
                ],width={"size": 6, "offset": 0}),
            ]),
        ], width=9),
        dbc.Col([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.Label(['Parametros'],style={'font-weight': 'bold', "text-align": "left"})),
                    dbc.CardBody([
                        html.Label(['Tipo de Declinacion:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                            id='dpd-decline-type',
                            options=[
                                {'label': 'Hiperbolica', 'value': 'HYP'},
                                {'label': 'Armonica', 'value': 'ARM'},
                                {'label': 'Exponencial', 'value': 'EXP'}
                            ],
                            value='HYP',
                            clearable=False,
                        ),
                        html.Br(),
                        html.Label(['Periodo Estable: '],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.DatePickerSingle(
                            id='dtp-start-date',
                            date=date.today(),
                            display_format='YYYY-MM-DD',
                        ),
                        dcc.DatePickerSingle(
                            id='dtp-end-date',
                            date=date.today(),
                            display_format='YYYY-MM-DD',
                        ),
                        html.Br(),
                        html.Br(),
                        html.Label(['Total Dias:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dbc.Input(id="inp-total-days", value=3000, type="text", style={'backgroundColor':'white'}),
                        html.Br(),
                    ]),
                ]),
                dbc.Card([
                    dbc.CardHeader(html.Label(['Resultados'],style={'font-weight': 'bold', "text-align": "left"})),
                    dbc.CardBody([
                        dbc.Row([
                            html.Label(['Tasa inicial Prod.: '],style={'font-weight': 'bold', "text-align": "left", "margin-left": "15px"}),
                            html.Div(id="txt-initial-rate"),
                        ]),
                        dbc.Row([
                            html.Label(['Última tasa Prod.: '],style={'font-weight': 'bold', "text-align": "left", "margin-left": "15px"}),
                            html.Div(id="txt-last-rate"),
                        ]),
                        dbc.Row([
                            html.Label(['Tasa inicial Decli.: '],style={'font-weight': 'bold', "text-align": "left", "margin-left": "15px"}),
                            html.Div(id="txt-decline-rate"),
                        ]),
                        dbc.Row([
                            html.Label(['Coeficiente declinacion: '],style={'font-weight': 'bold', "text-align": "left", "margin-left": "15px"}),
                            html.Div(id="txt-decline-coef"),
                        ]),
                        dbc.Row([
                            html.Label(['Maximo Qp: '],style={'font-weight': 'bold', "text-align": "left", "margin-left": "15px"}),
                            html.Div(id="txt-max-qp"),
                        ]),
                    ])
                ]),
            ]),
        ], width=3),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.Label(['Resultados'],style={'font-weight': 'bold', "text-align": "left"})),
                dbc.CardBody([

                ])
            ]),
        ]),
    ]),
])

@app.callback(
    [Output('cht-decline-chart','figure'),
    Output('cht-cumulative-chart','figure'),
    Output('txt-initial-rate','children'),
    Output('txt-last-rate','children'),
    Output('txt-decline-rate','children'),
    Output('txt-decline-coef','children'),
    Output('txt-max-qp','children')],
    [Input("btn_show_data_prod", "n_clicks"),
     Input("btn_run_forecast", "n_clicks"),
     Input('dpd-well-list', 'value'),
     Input('dpd-decline-type', 'value'),
     Input('inp-total-days', 'value'),
     Input('dtp-start-date', 'date'),
     Input('dtp-end-date', 'date')]) 
def update_line_chart(n_clicks1, n_clicks2, well_name, decline_type, total_days,start_date, end_date):

    data_results = pd.DataFrame()
    quer= ''
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    fig1 = go.Figure()
    fig2 = go.Figure()
    qi_val = ''
    b_val = ''
    max_qp = ''
    min_forecast = ''
    di_val = ''

    if 'btn_show_data_prod' in changed_id:
        #Filtra los datos por pozo y valores en diferentes a cero
        daily_prod_well = daily_prod[daily_prod['NOMBRE']==well_name]
        daily_prod_well= daily_prod_well[daily_prod_well['TASA_GAS'] != 0]

        #Construye grafico de declinacion
        fig1.add_trace(
            go.Scatter(x=daily_prod_well['FECHA'],
                y=daily_prod_well['TASA_GAS'],
                mode='lines',
                name='Datos de Produccion',
            ),
        ),
        fig1.update_xaxes(title_text="Fecha"),
        fig1.update_yaxes(title_text="Tasa (SCF/d)"),
        fig1.update_layout(legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ))
        fig1.update_layout(
                    autosize=True,
                    margin=dict(
                        l=50,
                        r=50,
                        b=50,
                        t=50,
                        pad=4
                    ),
                   )

    if 'btn_run_forecast' in changed_id:

        #Filtra los datos por pozo y valores en diferentes a cero
        daily_prod_well = daily_prod[daily_prod['NOMBRE']==well_name]
        daily_prod_well= daily_prod_well[daily_prod_well['TASA_GAS'] > 0]

        # convert date string to Panda datetime format
        daily_prod_well['FECHA'] =  pd.to_datetime(daily_prod_well['FECHA'], format='%Y-%m-%d') 

        #Filtrado por perido estable
        df_filter = daily_prod_well[(daily_prod_well['FECHA'] > start_date) & (daily_prod_well['FECHA'] < end_date)]

        raw_q = daily_prod_well['TASA_GAS']

        t = df_filter['FECHA']
        q = df_filter['TASA_GAS']


        #Define fix variables
        total_days = 3000

        # subtract one datetime to another datetime
        timedelta = [j-i for i, j in zip(t[:-1], t[1:])]
        timedelta = np.array(timedelta)
        timedelta = timedelta / datetime.timedelta(days=1)

        # take cumulative sum over timedeltas
        t = np.cumsum(timedelta)
        t = np.append(0, t)
        t = t.astype(float)

        # normalize the time and rate data
        t_normalized = t / max(t)
        q_normalized = q / max(q)

        if (decline_type=="HYP"):
            popt, pcov = curve_fit(hyperbolic, t_normalized, q_normalized, maxfev=100000)
            qi, di, b = popt
        elif (decline_type=="EXP"):
            popt, pcov = curve_fit(exponential, t_normalized, q_normalized, maxfev=100000)
            qi, di = popt
            b = 0
        elif (decline_type=="ARM"):
            popt, pcov = curve_fit(harmonic, t_normalized, q_normalized, maxfev=100000)
            qi, di = popt
            b = 1
 
        # de-normalize qi and di
        qi = qi * max(q)
        di = di / max(t)

        # forecast gas rate until 1,500 days
        t_forecast = np.arange(total_days)
        if (decline_type=="HYP"):
            q_forecast = hyperbolic(t_forecast, qi, di, b)
        elif (decline_type=="EXP"):
            q_forecast = exponential(t_forecast, qi, di)
        elif (decline_type=="ARM"):
            q_forecast = harmonic(t_forecast, qi, di)

        # forecast cumulative production until 1,500 days
        Qp_forecast = cumpro(q_forecast, qi, di, b)
        Max_Qp_Forecast = max(Qp_forecast)

        qi_val ='{} MMSCF'.format(np.round(qi, 3))
        min_forecast = '{} MMSCF'.format(np.round(min(q_forecast), 3))
        di_val = '{} SCF/D'.format(np.round(di, 3))
        b_val = '{}'.format(np.round(b, 3))
        max_qp = '{} MMSCF'.format(np.round(Max_Qp_Forecast, 3))

        #Construye grafico de declinacion
        fig1.add_trace(
            go.Scatter(x=t,
                y=q,
                mode='markers',
                name='Datos de Produccion',
            ),
        ),
        fig1.add_trace(
            go.Scatter(x=t_forecast,
                y=q_forecast,
                name='Pronostico',
            ),
        ),
        fig1.update_layout(legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ))
        fig1.update_xaxes(title_text="Dias Produccion"),
        fig1.update_yaxes(title_text="Tasa (SCF/d)"),
        fig1.update_layout(
            autosize=True,
            margin=dict(
                l=50,
                r=50,
                b=50,
                t=50,
                pad=4
            ),
            )

        #Construye grafico de acumulado
        fig2.add_trace(
            go.Scatter(x=t_forecast,
                y=Qp_forecast,
                name='Acumulado',
            ),
        ),
        fig2.update_xaxes(title_text="Dias Produccion"),
        fig2.update_yaxes(title_text="Produccion (SCF)"),

        fig2.update_layout(legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ))
        fig2.update_layout(
            autosize=True,
            margin=dict(
                l=50,
                r=50,
                b=50,
                t=50,
                pad=4
            ),
            )

    return fig1, fig2, qi_val, min_forecast, di_val, b_val, max_qp