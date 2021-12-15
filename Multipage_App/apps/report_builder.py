import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Row import Row
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash_table.Format import Format, Symbol
import dash_admin_components as dac
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
from datetime import datetime, tzinfo, timezone, timedelta, date
import dash_daq
import base64
import json
import os

from app import app 

#Variable con la ruta para salvar los querys
QUERY_DIRECTORY = "./querys"

#Lee el archivo de configuracion
configuracion = configparser.ConfigParser()

#Variable con la ruta para salvar los querys
QUERY_DIRECTORY = "./querys"
TEMPLATE_DIRECTORY = "./template/"
EXPORT_DIRECTORY = "./export/"

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

query = "SELECT NOMBRE FROM VARIABLES"
var_list =pd.read_sql(query, con)
var_list = var_list.sort_values('NOMBRE')['NOMBRE'].unique()

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
                            id='dpd-well-lista',
                            options=[{'label': i, 'value': i} for i in well_list],
                            clearable=False,
                            multi = True
                        ),
                    ], width={"size": 3, "offset": 0}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button(html.Span(["Ejecutar", html.I(className="far fa-file-alt ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                         id="btn_execute_report", color="success", className="mr-3"),
                    ], width={"size": 1, "offset": 1}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button(html.Span(["Exportar", html.I(className="fas fa-file-export ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                         id="btn_export_excel", color="warning", className="mr-3"),
                    ], width={"size": 1, "offset": 1}),
                ]),
                html.Br(),
            ]),
        ], width={"size": 8, "offset": 0}),
        dbc.Col([
            dbc.Card([
                dbc.Row([
                    dbc.Col([
                        html.Label(['Nombre Archivo:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dbc.Input(id="inp-ruta-report", placeholder="Type something...", type="text", style={'backgroundColor':'white'}),
                    ], width={"size": 3, "offset": 1}),
                    dbc.Col([
                        html.Br(),
                        dcc.Upload(
                            dbc.Button(html.Span(["Abrir", html.I(className="fas fa-upload ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                              color="warning", className="mr-3"),
                            id="btn_open_report",
                            multiple=False
                        ),
                    ], width={"size": 1, "offset": 0}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button(html.Span(["Salvar", html.I(className="fas fa-save ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                         id="btn_save_report", color="warning", className="mr-3"),
                        html.Div(id="save_message_reporte"),
                    ], width={"size": 1, "offset": 1}),
                ]),
                html.Br(),
            ]),
        ], width={"size": 4, "offset": 0}),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dac.Box([
                    dac.BoxHeader(
                        collapsible = False,
                        closable = False,
                        title="Reporte"
                    ),
                    dac.BoxBody([
                        dbc.Spinner(
                            dash_table.DataTable(id="dt_report_results", 
                            style_as_list_view=True,
                            style_cell={'padding': '5px', 'textAlign':'left','fontSize':15, 'font-family':'arial'},
                            style_header={
                                'backgroundColor': 'blue',
                                'fontWeight': 'bold',
                                'color': 'white',
                                'fontSize':15,
                                'font-family':'arial'
                            },
                            style_table={'overflowX': 'auto'},
                            editable=False,
                            filter_action="native",
                            sort_action="native",
                            sort_mode="multi",
                            column_selectable="single",
                            page_action="native",
                            page_current= 0,
                            page_size= 20,),
                        ),
                    ]),	
                ],
                color='primary',
                solid_header=True,
                elevation=4,
                width=12
            ),
        ], width=9),
        dbc.Col([
            dac.Box([
                    dac.BoxHeader(
                        collapsible = False,
                        closable = False,
                        title="Opciones"
                    ),
                    dac.BoxBody([
                        dcc.Checklist(
                            id='ckl-group-by',
                            options=[
                                {'label': 'Aplicar agrupación por: ', 'value': 'GBY'},
                            ],
                        ),
                        dcc.Dropdown(
                            id='dpd-group-by',
                            options=[
                                {'label': 'NOMBRE', 'value': 'NOMBRE'},
                                {'label': 'FECHA', 'value': 'FECHA'},
                            ],
                            multi=True,
                        ),
                        dcc.RadioItems(
                            id='rb-aggregation',
                            options=[
                                {'label': 'Sumatoria  ', 'value': 'SUM'},
                                {'label': 'Media', 'value': 'MEAN'},
                            ],
                            value='SUM',
                        ),
                        html.Br(),
                        dbc.Row([
                            dbc.Col([
                                dcc.RadioItems(
                                    id='rb-filter-date',
                                    options=[
                                        {'label': ' Todo', 'value': 'ALL'},
                                        {'label': ' A la Fecha', 'value': 'ATDATE'},
                                        {'label': ' Última Fecha', 'value': 'LASTDATE'},
                                        {'label': ' Rango Fecha', 'value': 'RANGE'},
                                    ],
                                    value='ALL',
                                ),
                                html.Br(),
                                dcc.Checklist(
                                    id='ckl-clear-report-data',
                                    options=[
                                        {'label': ' Limpiar valores cero', 'value': 'CERO'},
                                    ],
                                ),
                                html.Br(),
                            ]),
                            dbc.Col([
                                html.Label(['Ordenado por: '],style={'font-weight': 'bold', "text-align": "left"}),
                                dcc.Dropdown(
                                    id='dpd-order-by',
                                    options=[
                                        {'label': 'NOMBRE', 'value': 'NOMBRE'},
                                        {'label': 'FECHA', 'value': 'FECHA'},
                                    ],
                                    multi=True,
                                ),
                                dash_daq.BooleanSwitch(
                                    on=False,
                                    id='bs-order-by',
                                    label="Ascendente",
                                    labelPosition="top"
                                    )
                            ]),
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    html.Label(['Fecha: '],style={'font-weight': 'bold', "text-align": "left"}),
                                    dcc.DatePickerSingle(
                                        id='dtp_fecha_filter_report',
                                        date=date.today(),
                                        display_format='YYYY-MM-DD',
                                        style={'backgroundColor':'white'},
                                    ),
                                    html.Br(),
                                    html.Label(['Rango: '],style={'font-weight': 'bold', "text-align": "left"}),
                                    dcc.DatePickerRange(
                                        id='dtp_fecha_filter_range_report',
                                        min_date_allowed=date(1995, 1, 1),
                                        max_date_allowed=date.today(),
                                        start_date = date.today()- timedelta(days=-7),
                                        end_date=date.today(),
                                        display_format='YYYY-MM-DD',
                                        style={'backgroundColor':'white'},
                                    ),
                                ]),
                            ]),
                            html.Br(),
                            html.Label(['Variable Calculadas:'],style={'font-weight': 'bold', "text-align": "left"}),
                            dcc.Dropdown(
                                id='dpd-var-list',
                                options=[{'label': i, 'value': i} for i in var_list],
                                clearable=False,
                                multi=True,
                            ),
                    ]),	
                ],
                color='primary',
                solid_header=True,
                elevation=4,
                width=12
            ),
        ], width=3),
    ]),
])

@app.callback(
    [Output("dt_report_results", "data"), Output("dt_report_results", "columns")],
    [Input("btn_execute_report", "n_clicks"),
     Input('dpd-query-lista', 'value'), 
     Input('dpd-well-lista', 'value'),
     Input('dpd-var-list', 'value'),
     Input('ckl-group-by', 'value'),
     Input('dpd-group-by', 'value'),
     Input('rb-aggregation', 'value'),
     Input('rb-filter-date', 'value'),
     Input('dtp_fecha_filter_report', 'date'),
     Input('dtp_fecha_filter_range_report', 'start_date'),
     Input('dtp_fecha_filter_range_report', 'end_date'), 
     Input('dpd-order-by', 'value'),
    Input('bs-order-by', 'on')], 
    [State('dt_report_results', 'data'), State('dt_report_results', 'columns')]
)
def update_table(n_clicks, file_name, well_name, var_list, group_by, group_options, agregation_fun, filter_date_type, at_date,start_date, end_date, order_by, ascendente, data, columns):
    df = pd.DataFrame()
    data_frame = pd.DataFrame()
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

    if 'btn_execute_report' in changed_id:
        con = sqlite3.connect(archivo)
        query = "SELECT * FROM VARIABLES"
        variables =pd.read_sql(query, con)
        query=''
        if file_name is not None:
            with open(os.path.join(QUERY_DIRECTORY, file_name)) as f:
                contenido = f.readlines()
            if contenido is not None:
                for linea in contenido:
                    query +=  linea
            
                #Filtra el dataframe en un rango de fechas
                if filter_date_type == 'RANGE' and start_date and end_date:
                    query += " WHERE DATE(FECHA)>='"+start_date+"' AND DATE(FECHA)<='"+end_date+"'"

                df =pd.read_sql(query, con)

                if order_by:
                    df = df.sort_values(by=order_by, ascending=ascendente)

                #Extrae la maxima fecha
                data_frame['FECHA'] = pd.to_datetime(df['FECHA'])
                last_date = str(data_frame['FECHA'].max())
                time_last_date = last_date[-9:]
                
                #Filtra el dataframe a una fecha determinada
                if filter_date_type == 'ATDATE' and at_date:
                    df= df.loc[df['FECHA']==at_date+time_last_date]

                #Filtra el dataframe a la ultima fecha
                if filter_date_type == 'LASTDATE' and at_date:
                    df= df.loc[df['FECHA']==last_date]

                if well_name:
                    df= df.loc[df['NOMBRE'].isin(well_name)]

                df = df.drop(['index'], axis=1)

                if group_by:
                    if agregation_fun == 'SUM':
                        df =df.groupby(group_options, as_index=True).sum().reset_index()
                    else:
                        df =df.groupby(group_options, as_index=True).mean().reset_index()
            if var_list:
                for var in var_list:
                    selec_var=variables.loc[variables['NOMBRE']==var]
                    ecuacion = selec_var.iloc[0]['ECUACION']
                    titulo = selec_var.iloc[0]['TITULO']
                    evalu = eval(ecuacion)
                    df[titulo] = evalu

    columns = [{'name': i, 'id': i, "deletable": True} for i in df.columns]
    data = df.to_dict('records')

    return data, columns

@app.callback(
    Output('save_message_reporte','children'),
    [Input('btn_save_report', 'n_clicks'),
    Input('dpd-query-lista', 'value'),
    Input('inp-ruta-report', 'value'),
    Input('dpd-var-list', 'value')]) 
def save_reporte(n_clicks, consulta, file_name, var_list ):
    mensaje=''
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'btn_save_report' in changed_id:
        data = {}
        data['reporte'] = []
        data['reporte'].append({
            'consulta': consulta,
            'var_list': var_list})
        with open(TEMPLATE_DIRECTORY+file_name, 'w') as file:
            json.dump(data, file, indent=4)
        mensaje = 'Archivo guardado'
    return mensaje

@app.callback( [Output('inp-ruta-report', 'value'),
                Output('dpd-query-lista', 'value'),
                Output('dpd-var-list', 'value')],
              [Input('btn_open_report', 'filename'),
              Input('btn_open_report', 'contents')]
              )
def open_report( list_of_names, list_of_contents):
    archivo = list_of_names
    consulta=[]
    var_list=[]

    if list_of_names is not None:
        print(list_of_names)
        archivo = list_of_names
        with open(TEMPLATE_DIRECTORY+archivo) as file:
            data = json.load(file)
            for drop_values   in data['reporte']:
                consulta = str(drop_values['consulta'])
                var_list = drop_values['var_list']
    return archivo, consulta, var_list