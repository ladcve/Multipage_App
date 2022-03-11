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
import numpy as np
import pandas as pd
from datetime import datetime, tzinfo, timezone, timedelta, date
from collections import OrderedDict
import base64
import json
import os
import datetime
from scipy.optimize import curve_fit

from app import app
from library import hyperbolic, exponential, harmonic, cumpro, listToString

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

#Crea dataframe con datos de produccion
query = "SELECT NOMBRE, FECHA, TASA_GAS, ACUM_GAS, TASA_CONDENSADO, ACUM_CONDESADO FROM CIERRE_DIARIO_POZO WHERE TASA_GAS>0 ORDER BY FECHA "
daily_prod =pd.read_sql(query, con)
daily_prod['FECHA'] =  pd.to_datetime(daily_prod['FECHA'], format='%Y-%m-%d') 

#Maxima fecha de produccion
MAX_FECHA =daily_prod['FECHA'].max()

con.close()


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
                        ),
                    ], width={"size": 2, "offset": 1}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button(html.Span(["mostrar ", html.I(className="fas fa-chart-line-down ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                         id="btn_show_data_prod", color="primary", className="mr-3"),
                    ], width={"size": 1, "offset": 0}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button(html.Span(["Pronostico ", html.I(className="fas fa-running ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                         id="btn_run_forecast", color="primary", className="mr-3"),
                    ], width={"size": 1, "offset": 1}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button(html.Span(["Grabar ", html.I(className="fas fa-save ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                         id="btn_save_forecast", color="success", className="mr-3"),
                        html.Div(id="save_message_forecast"),
                    ], width={"size": 1, "offset": 2}),
                ]),
                html.Br(),
            ], style={"background-color": "#F9FCFC"},),
        ], width={"size": 6, "offset": 0}),
        dbc.Col([
            dbc.Card([
                dbc.Row([
                    dbc.Col([
                        html.Label(['Nombre Plantilla:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dbc.Input(id="inp-ruta-decline", placeholder="Type something...", type="text", style={'backgroundColor':'white'}),
                    ], width={"size": 4, "offset": 1}),
                     dbc.Col([
                        html.Br(),
                        dcc.Upload(
                            dbc.Button(html.Span(["Abrir ", html.I(className="fas fa-upload ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                             n_clicks=0, color="primary", className="mr-3"),
                            id='btn_open_decline',
                            multiple=False
                        ),
                    ], width={"size": 2, "offset": 0}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button(html.Span(["Grabar ", html.I(className="fas fa-save ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                         id="btn_save_decline", n_clicks=0, color="primary", className="mr-3"),
                        html.Div(id="save_message_decline"),
                    ], width={"size": 2, "offset": 1}),
                ]),
                html.Br(),
            ], style={"background-color": "#F9FCFC"},),
        ], width={"size": 4, "offset": 0}),
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
                                title="Curva de Declinación"
                            ),
                            dac.BoxBody([
                                dcc.Loading(
                                    dcc.Graph(id='cht-decline-chart'),
                                ),
                            ]),	
                        ],
                        color='primary',
                        solid_header=True,
                        elevation=4,
                        width=12
                    ),
                ], width={"size": 6, "offset": 0}),
                dbc.Col([
                    dac.Box([
                            dac.BoxHeader(
                                collapsible = False,
                                closable = False,
                                title="Curva de Acumulado"
                            ),
                            dac.BoxBody([
                                dcc.Loading(
                                    dcc.Graph(id='cht-cumulative-chart'),
                                ),
                            ]),	
                        ],
                        color='primary',
                        solid_header=True,
                        elevation=4,
                        width=12
                    ),
                ],width={"size": 6, "offset": 0}),
            ]),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dac.Box([
                            dac.BoxHeader(
                                collapsible = False,
                                closable = False,
                                title="Resultados"
                            ),
                            dac.BoxBody([
                                dash_table.DataTable(id="dt_decline", 
                                    style_as_list_view=True,
                                    style_cell={'padding': '5px'},
                                    style_header={
                                        'backgroundColor': 'blue',
                                        'fontWeight': 'bold',
                                        'color': 'white'
                                    },
                                    style_table={'overflowX': 'auto'},
                                    editable=False,
                                    filter_action="native",
                                    sort_action="native",
                                    sort_mode="multi",
                                    column_selectable="single",
                                    page_action="native",
                                    page_current= 0,
                                    page_size= 20
                                ),
                            ]),	
                        ],
                        color='primary',
                        solid_header=True,
                        elevation=4,
                        width=12
                    ),
                ]),
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
                            dbc.Row([
                                dbc.Col([
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
                                    html.Label(['Fase:'],style={'font-weight': 'bold', "text-align": "left"}),
                                    dcc.Dropdown(
                                        id='dpd-decline-data',
                                        options=[
                                            {'label': 'GAS', 'value': 'TASA_GAS'},
                                            {'label': 'CONDENSADO', 'value': 'TASA_CONDENSADO'},
                                        ],
                                        value='TASA_GAS',
                                        clearable=False,
                                    ),
                                    html.Br(),
                                    html.Label(['Periodo Estable: '],style={'font-weight': 'bold', "text-align": "left"}),
                                    dcc.DatePickerSingle(
                                        id='dtp-start-date',
                                        date=MAX_FECHA - timedelta(days=30),
                                        display_format='YYYY-MM-DD',
                                    ),
                                    dcc.DatePickerSingle(
                                        id='dtp-end-date',
                                        date=MAX_FECHA,
                                        display_format='YYYY-MM-DD',
                                    ),
                                    html.Br(),
                                    daq.ToggleSwitch(
                                        id='ts-value-filter',
                                        value=False,
                                        label='Filtrar valores',
                                        labelPosition='top'
                                    ),
                                ]),
                            ]),	
                            dbc.Row([
                                dbc.Col([
                                    html.Label(['Minimo:'],style={'font-weight': 'bold', "text-align": "left"}),
                                    dbc.Input(id="inp-minimo", type="number", step=1, style={'backgroundColor':'white'}),
                                    html.Br(),
                                ]),
                                dbc.Col([
                                    html.Label(['Maximo:'],style={'font-weight': 'bold', "text-align": "left"}),
                                    dbc.Input(id="inp-maximo", type="number", step=1, style={'backgroundColor':'white'}),
                                    html.Br(),
                                ]),
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    html.Br(),
                                    daq.ToggleSwitch(
                                        id='ts-end-days',
                                        value=False,
                                        label='Usar Dias or Fecha',
                                        labelPosition='top'
                                    ),
                                ]),
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    html.Label(['Total Dias:'],style={'font-weight': 'bold', "text-align": "left"}),
                                    dbc.Input(id="inp-total-days", value=3000, type="number", step=1, style={'backgroundColor':'white'}),
                                    html.Br(),
                                ]),
                                dbc.Col([ 
                                    html.Label(['Fecha: '],style={'font-weight': 'bold', "text-align": "left"}),
                                    dcc.DatePickerSingle(
                                        id='dtp_max_date',
                                        date=MAX_FECHA + timedelta(days=3000),
                                        display_format='YYYY-MM-DD',
                                        style={'backgroundColor':'white'},
                                    ),
                                ]),
                            ]),
                        ]),	
                    ],
                    color='primary',
                    solid_header=True,
                    elevation=4,
                    width=12,
                    style={"background-color": "#F9FCFC"},
                ),
                dac.Box([
                        dac.BoxHeader(
                            collapsible = False,
                            closable = False,
                            title="Resultados"
                        ),
                        dac.BoxBody([
                            dbc.Row([
                                html.Label(['Tasa inicial Prod.: '],style={'font-weight': 'bold', "text-align": "left", "margin-left": "15px"}),
                                html.Label(html.Div(id="txt-initial-rate"),style={'font-weight': 'bold', 'color':'blue', "text-align": "left", "margin-left": "15px"}),
                            ]),
                            dbc.Row([
                                html.Label(['Última tasa Prod.: '],style={'font-weight': 'bold', "text-align": "left", "margin-left": "15px"}),
                                html.Label(html.Div(id="txt-last-rate"),style={'font-weight': 'bold', 'color':'blue', "text-align": "left", "margin-left": "15px"}),
                            ]),
                            dbc.Row([
                                html.Label(['Tasa inicial Decli.: '],style={'font-weight': 'bold', "text-align": "left", "margin-left": "15px"}),
                                html.Label(html.Div(id="txt-decline-rate"),style={'font-weight': 'bold', 'color':'blue', "text-align": "left", "margin-left": "15px"}),
                            ]),
                            dbc.Row([
                                html.Label(['Coeficiente declinacion: '],style={'font-weight': 'bold', "text-align": "left", "margin-left": "15px"}),
                                html.Label(html.Div(id="txt-decline-coef"),style={'font-weight': 'bold', 'color':'blue', "text-align": "left", "margin-left": "15px"}),
                            ]),
                            dbc.Row([
                                html.Label(['Tiempo inicial: '],style={'font-weight': 'bold', "text-align": "left", "margin-left": "15px"}),
                                html.Label(html.Div(id="txt-initial-time"),style={'font-weight': 'bold', 'color':'blue', "text-align": "left", "margin-left": "15px"}),
                            ]),
                            dbc.Row([
                                html.Label(['Tiempo final: '],style={'font-weight': 'bold', "text-align": "left", "margin-left": "15px"}),
                                html.Label(html.Div(id="txt-end-time"),style={'font-weight': 'bold', 'color':'blue', "text-align": "left", "margin-left": "15px"}),
                            ]),
                            dbc.Row([
                                html.Label(['EUR: '],style={'font-weight': 'bold', "text-align": "left", "margin-left": "15px"}),
                                html.Label(html.Div(id="txt-EUR"),style={'font-weight': 'bold', 'color':'blue', "text-align": "left", "margin-left": "15px"}),
                            ]),
                            dbc.Row([
                                html.Label(['Cumpro: '],style={'font-weight': 'bold', "text-align": "left", "margin-left": "15px"}),
                                html.Label(html.Div(id="txt-max-qp"),style={'font-weight': 'bold', 'color':'blue', "text-align": "left", "margin-left": "15px"}),
                            ]),
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
    dbc.Modal(
        [
            dbc.ModalHeader("Plantilla Salvada"),
        ],
        id="modal_save_decline",
        is_open=False,
    ),
    dbc.Modal(
        [
            dbc.ModalHeader("Datos Salvados a la BD."),
        ],
        id="modal_save_db",
        is_open=False,
    ),
])

@app.callback(
    [Output('cht-decline-chart','figure'),
    Output('cht-cumulative-chart','figure'),
    Output('txt-initial-rate','children'),
    Output('txt-last-rate','children'),
    Output('txt-decline-rate','children'),
    Output('txt-decline-coef','children'),
    Output('txt-max-qp','children'),
    Output('txt-EUR','children'),
    Output('txt-initial-time','children'),
    Output('txt-end-time','children'),
    Output('dt_decline','data'),
    Output('dt_decline','columns')],
    [Input("btn_show_data_prod", "n_clicks"),
     Input("btn_run_forecast", "n_clicks"),
     Input('dpd-well-list', 'value'),
     Input('dpd-decline-type', 'value'),
     Input('inp-total-days', 'value'),
     Input('dtp-start-date', 'date'),
     Input('dtp-end-date', 'date'),
     Input('ts-end-days', 'value'),
     Input('dtp_max_date', 'date'),
     Input('dpd-decline-data', 'value'),
     Input('inp-total-days', 'value'),
     Input('ts-value-filter','value'),
     Input('inp-minimo','value'),
     Input('inp-maximo','value')]) 
def update_line_chart(n_clicks1, n_clicks2, well_name, decline_type, total_days,start_date, end_date, ts_days, decl_end_date, decl_data, decl_days, filter_data, minimo, maximo):

    data_results = pd.DataFrame()
    query= ''
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    fig1 = go.Figure()
    fig2 = go.Figure()
    qi_val = ''
    b_val = ''
    max_qp = ''
    min_forecast = ''
    di_val = ''
    EUR = ''
    ti=''
    acum_gas = 0
    columns = [],
    data=[]
    max_decl_date = ''
    table_results = pd.DataFrame()

   
    #Listado de unidades por variables
    con = sqlite3.connect(archivo)
    query = "SELECT * FROM UNIDADES"
    unidades =pd.read_sql(query, con)
    selec_unit = unidades.set_index(['VARIABLE'])


    if 'btn_show_data_prod' in changed_id:
        decl_end_date = decl_end_date.replace("T00:00:00","")
        decl_end_date = datetime.datetime.strptime( decl_end_date, '%Y-%m-%d')

        #Filtra los datos por pozo y valores en diferentes a cero
        daily_prod_well = daily_prod[daily_prod['NOMBRE']==well_name]
        daily_prod_well.drop('NOMBRE', inplace=True, axis=1)

        #Filtrado por rango de valores
        if filter_data and minimo and maximo:
            daily_prod_well = daily_prod_well[(daily_prod_well[decl_data] >= minimo) & (daily_prod_well[decl_data] <= maximo)]

        var_title = selec_unit.loc[decl_data]['GRAFICO']
        var_unit = selec_unit.loc[decl_data]['UNIDAD']
        var_color = selec_unit.loc[decl_data]['COLOR']
        var_name = var_title + " " + var_unit
        color_axis = dict(hex=var_color)
 
        #Construye grafico de declinacion
        fig1.add_trace(
            go.Scatter(x=daily_prod_well['FECHA'],
                y=daily_prod_well[decl_data],
                mode='lines',
                line_color=color_axis["hex"],
                name='Datos de Produccion',
            ),
        ),

        fig1.update_xaxes(title_text="Fecha"),
        fig1.update_yaxes(title_text=var_name),
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

        if well_name:
            #Filtra los datos por pozo y valores en diferentes a cero
            daily_prod_well = daily_prod[daily_prod['NOMBRE']==well_name]

            #Filtrado por perido estable
            df_filter = daily_prod_well[(daily_prod_well['FECHA'] > start_date) & (daily_prod_well['FECHA'] < end_date)]

            #Filtrado por rango de valores
            if filter_data and minimo and maximo:
                df_filter = df_filter[(df_filter[decl_data] >= minimo) & (df_filter[decl_data] <= maximo)]

            raw_q = daily_prod_well[decl_data]
            ti = df_filter['FECHA'].min()

            t = df_filter['FECHA']
            q = df_filter[decl_data]

            if decl_data=='TASA_GAS':
                acum_gas = daily_prod_well["ACUM_GAS"].max()
            if decl_data=='TASA_CONDENSADO':
                acum_gas = daily_prod_well["ACUM_CONDESADO"].max()

            #Define fix variables
            if ts_days:
                total_days = (decl_end_date - MAX_FECHA).days
            else:
                total_days = decl_days

            max_decl_date = MAX_FECHA + datetime.timedelta(days=int(total_days))

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

            # forecast gas rate until decline days
            t_forecast = np.arange(total_days)
            if (decline_type=="HYP"):
                q_forecast = hyperbolic(t_forecast, qi, di, b)
            elif (decline_type=="EXP"):
                q_forecast = exponential(t_forecast, qi, di)
            elif (decline_type=="ARM"):
                q_forecast = harmonic(t_forecast, qi, di)

            # forecast cumulative production 
            Qp_forecast = cumpro(q_forecast, qi, di, b)
            Max_Qp_Forecast = max(Qp_forecast)

            qi_val ='{} MMSCF'.format(np.round(qi, 3))
            min_forecast = '{} MMSCF'.format(np.round(min(q_forecast), 3))
            di_val = '{} SCF/D'.format(np.round(di, 6))
            b_val = '{}'.format(np.round(b, 3))
            max_qp = '{} MMSCF'.format(np.round(Max_Qp_Forecast, 3))
            EUR = '{} MMSCF'.format(np.round(Max_Qp_Forecast + acum_gas, 6))
            

            #tabla de resultados
            table_results['DIAS']=t_forecast
            table_results['PRONOSTICO']=q_forecast
            table_results['NOMBRE']=well_name

            if (decline_type=="HYP"):
                table_results['DECLINACION']="HIPERBOLICA"
            elif (decline_type=="EXP"):
                table_results['DECLINACION']="EXPONENIAL"
            elif (decline_type=="ARM"):
                table_results['DECLINACION']="ARMONICA"     

            #table_results['FECHA']=timedelta(days=t_forecast)+MAX_FECHA

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
            fig1.update_yaxes(title_text="Tasa (SCF/d)", type="log"),
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

    columns = [{'name': i, 'id': i} for i in table_results.columns]
    data=table_results.to_dict('records')
    return fig1, fig2, qi_val, min_forecast, di_val, b_val, max_qp, EUR, ti, max_decl_date, data, columns

@app.callback(
    Output('modal_save_decline','is_open'),
    [Input('btn_save_decline', 'n_clicks'),
    Input('dpd-decline-type', 'value'),
    Input('dtp-start-date', 'date'),
    Input('dtp-end-date', 'date'),
    Input('inp-ruta-decline', 'value'),
    Input('inp-total-days', 'value'),
    Input('dtp_max_date', 'date')],
    State('modal_map', 'is_open')) 
def save_decline(n_clicks, tipo_decl, start_date, end_date, file_name, decl_days, decl_end_date, is_open ):
    mensaje=''
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'btn_save_decline' in changed_id:
        data = {}
        data['grafico'] = []
        data['grafico'].append({
            'declinacion': tipo_decl,
            'start_date': start_date,
            'end_date': end_date,
            'decl_days': decl_days,
            'decl_end_date': decl_end_date,})
        if file_name:
            with open(TEMPLATE_DIRECTORY+file_name, 'w') as file:
                json.dump(data, file, indent=4)
            is_open = True
    return is_open

@app.callback( [Output('inp-ruta-decline', 'value'),
                Output('dpd-decline-type', 'value'),
                Output('dtp-start-date', 'date'),
                Output('dtp-end-date', 'date'),
                Output('inp-total-days', 'value'),
                Output('dtp_max_date', 'date')],
              [Input('btn_open_decline', 'n_clicks'),
              Input('btn_open_decline', 'filename'),
              Input('btn_open_decline', 'contents')]
              )
def open_decline( n_clicks, list_of_names, list_of_contents):
    archivo = list_of_names
    declinacion='HYP'
    start_date=MAX_FECHA - timedelta(days=30)
    end_date=MAX_FECHA
    decl_days=3000
    decl_end_date=MAX_FECHA + timedelta(days=3000)

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

    if 'btn_open_decline' in changed_id:
        if list_of_names is not None:
            print(list_of_names)
            archivo = list_of_names
            with open(TEMPLATE_DIRECTORY+archivo) as file:
                data = json.load(file)
                for drop_values   in data['grafico']:
                    declinacion = str(drop_values['declinacion'])
                    start_date = listToString(drop_values['start_date'])
                    end_date = listToString(drop_values['end_date'])
                    decl_days = drop_values['decl_days']
                    decl_end_date = listToString(drop_values['decl_end_date'])

    return archivo, declinacion, start_date, end_date, decl_days, decl_end_date

@app.callback(
    Output("modal_save_db", "is_open"),
    Input("btn_save_forecast", "n_clicks"),
    [State('dt_decline', 'data'), State('modal_save_db', 'is_open')]
)
def fupdate_table(n_clicks, dataset, is_open):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

    pg = pd.DataFrame(dataset)
    if 'btn_save_forecast' in changed_id:
        con = sqlite3.connect(archivo)
        pg.to_sql('DCA', con, if_exists='append', index=False)
        con.commit()
        con.close()
        is_open=True
    return is_open