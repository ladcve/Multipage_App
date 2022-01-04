import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Row import Row
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ALL, MATCH
import dash_admin_components as dac
import plotly.express as px
from plotly.subplots import make_subplots
import dash_table
import sqlite3
import configparser
import sys
import os.path
import os
from os import listdir
from os.path import isfile, join
import pandas as pd
from datetime import date
from collections import OrderedDict
import base64
import json
import os

from app import app 

#https://community.plotly.com/t/pattern-call-backs-regarding-adding-dynamic-graphs/40724/4

#Variable con la ruta para salvar los querys
QUERY_DIRECTORY = "./querys"

#Lee el archivo de configuracion
configuracion = configparser.ConfigParser()

#Variable con la ruta para salvar los querys
QUERY_DIRECTORY = "./querys"
CHART_DIRECTORY = "./template/"

# padding for the page content
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

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

con.close()

#Listado de query
pathway = './querys'
files = [f for f in listdir(pathway) if isfile(join(pathway, f))]

file_name = ''
df = pd.DataFrame()


content = html.Div(id="container", children=[], style=CONTENT_STYLE)

layout = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.Row([
                    dbc.Col([
                        html.Label(['Consulta:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                            id='dpd-query-list',
                            options=[
                                {'label': i, 'value': i} for i in files
                            ],
                            clearable=False
                        ),
                    ], width={"size": 4, "offset": 1}),
                    dbc.Col([
                        html.Label(['Pozo:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                            id='dpd-well-list',
                            options=[{'label': i, 'value': i} for i in well_list],
                            clearable=False
                        ),
                    ], width={"size": 4, "offset": 0}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button(html.Span(["Agregar ", html.I(className="fas fa-chart-bar ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                        id="btn_add_chart", color="success", className="mr-3"),
                    ]),
                ]),
                html.Br(),
            ]),
        ], width={"size": 6, "offset": 0}),
    ]),
    html.Br(),
    dac.Box([
        dac.BoxHeader(
            collapsible = False,
            closable = False,
            title="Gráficos de Líneas"
        ),
        dac.BoxBody(
            html.Div(content),
        )],
        color='primary',
        solid_header=True,
        elevation=4,
        width=12
    ),
])

def create_figure(column_x, column_y1, column_y2, well, file_name, color_y1, color_y2):
    sel_color_y1 = dict(hex='#0000ff')
    sel_color_y2 = dict(hex='#0000ff')
    if color_y1=='rojo':
        sel_color_y1 = dict(hex='#FF0000')
    if color_y1=='verde':
        sel_color_y1 = dict(hex='#008f39')
    if color_y2=='rojo':
        sel_color_y2 = dict(hex='#FF0000')
    if color_y2=='verde':
        sel_color_y2 = dict(hex='#008f39')
    query= ''
    con = sqlite3.connect(archivo)
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    if file_name:
        with open(os.path.join(QUERY_DIRECTORY, file_name)) as f:
            contenido = f.readlines()
            for linea in contenido:
                query +=  linea 
            df =pd.read_sql(query, con)
            df = df.query("NOMBRE == '{}'".format(well))
            df = df.sort_values(by='FECHA')
        con.close()
        fig = px.line(df, x=column_x, y=column_y1)
        fig.update_layout(
                title="{} {} vs {}".format(well, column_x, column_y1),
                hovermode='x unified',
                line_color=sel_color_y1["hex"],
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgb(240, 240, 240)',
            )
        for columnas_y2 in column_y2:
            fig.add_trace(
                px.Scatter(x=df['FECHA'],
                    y=df[columnas_y2],
                    name=columnas_y2,
                    line_color=sel_color_y1["hex"],
                    yaxis= 'y2'),
                secondary_y=True,
            )
        #fig.update_traces(line_color=color["hex"]) 
        fig.update_xaxes(title_text="",showline=True, linewidth=2, linecolor='black', showgrid=False,)
        fig.update_yaxes(title_text="",showline=True, linewidth=2, linecolor='black', showgrid=False,)
    return fig

@app.callback(
    Output("container", "children"),
    [
        Input("btn_add_chart", "n_clicks"),
        Input({"type": "dynamic-delete", "index": ALL}, "n_clicks"),
    ],
    [State("dpd-well-list", "value"),  State("dpd-query-list", "value"), State("container", "children")],
)
def display_dropdowns(n_clicks, _,  well, file_name, children):
    query = ''
    input_id = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
    if "index" in input_id:
        delete_chart = json.loads(input_id)["index"]
        children = [
            chart
            for chart in children
            if "'index': " + str(delete_chart) not in str(chart)
        ]
    else:
        default_column_x = "FECHA" 
        default_column_y1 = ""
        default_column_y2 = ""
        con = sqlite3.connect(archivo)
        if file_name:
            with open(os.path.join(QUERY_DIRECTORY, file_name)) as f:
                contenido = f.readlines()
                for linea in contenido:
                    query +=  linea 
                df =pd.read_sql(query, con)
                df = df.query("NOMBRE == '{}'".format(well))
                df =df.sort_values("FECHA")
            column_name_list = df.columns.values.tolist()
            default_column_y1 = column_name_list[3]
            default_column_y2 = column_name_list[3]
            default_color = 'Azul'
            
            new_element = html.Div([
                    dbc.Row([
                        dbc.Col([
                            dac.Box([
                                    dac.BoxBody([
                                        dcc.Graph(
                                            id={"type": "dynamic-output", "index": n_clicks},
                                            style={"width": "100%"},
                                            figure=create_figure(default_column_x, default_column_y1,default_column_y2, well, file_name, default_color, default_color),
                                        ),
                                    ]),	
                                ],
                                color='primary',
                                solid_header=True,
                                elevation=4,
                                width=12
                            ),

                        ], width={"size": 9, "offset": -1}),
                        dbc.Col([
                            html.Div(
                                dbc.Button(html.Span(["Borrar ", html.I(className="fas fa-trash-alt ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                                id={"type": "dynamic-delete", "index": n_clicks}, n_clicks=0, color="danger", className="mr-3"),
                                className="d-grid gap-2 d-md-flex justify-content-md-end"
                            ),
                            html.Br(),
                            dac.Box([
                                    dac.BoxHeader(
                                        collapsible = False,
                                        closable = False,
                                        title="Opciones:"
                                    ),
                                    dac.BoxBody([
                                        html.Br(),
                                        html.Label(['Eje X:'],style={'font-weight': 'bold', "text-align": "left"}),
                                        dcc.Dropdown(
                                            id={"type": "dynamic-drop-x", "index": n_clicks},
                                            options=[{"label": i, "value": i} for i in df.columns],
                                            value=default_column_x,
                                            clearable=False,
                                        ), 
                                        html.Br(),
                                        html.Label(['Eje Y:'],style={'font-weight': 'bold', "text-align": "left"}),
                                        dcc.Dropdown(
                                            id={"type": "dynamic-drop-y1", "index": n_clicks},
                                            options=[{"label": i, "value": i} for i in df.columns],
                                            value=default_column_y,
                                            clearable=False,
                                        ),
                                        html.Br(),
                                        html.Label(['Color Linea:'],style={'font-weight': 'bold', "text-align": "left"}),
                                        dcc.Dropdown(
                                            id={"type": "dynamic-color-picker-y1", "index": n_clicks},
                                            options=[
                                                {'label': 'Azul', 'value': 'azul'},
                                                {'label': 'Rojo', 'value': 'rojo'},
                                                {'label': 'Verde', 'value': 'verde'}
                                            ],
                                            value='azul',
                                        ),
                                        html.Br(),
                                        html.Label(['Eje Y:'],style={'font-weight': 'bold', "text-align": "left"}),
                                        dcc.Dropdown(
                                            id={"type": "dynamic-drop-y2", "index": n_clicks},
                                            options=[{"label": i, "value": i} for i in df.columns],
                                            value=default_column_y,
                                            clearable=False,
                                        ),
                                        html.Br(),
                                        html.Label(['Color Linea:'],style={'font-weight': 'bold', "text-align": "left"}),
                                        dcc.Dropdown(
                                            id={"type": "dynamic-color-picker-y2", "index": n_clicks},
                                            options=[
                                                {'label': 'Azul', 'value': 'azul'},
                                                {'label': 'Rojo', 'value': 'rojo'},
                                                {'label': 'Verde', 'value': 'verde'}
                                            ],
                                            value='azul',
                                        ),
                                    ]),	
                                ],
                                color='primary',
                                solid_header=True,
                                elevation=4,
                                width=12
                            ),
                        ], width={"size": 3, "offset": 0}),
                    ]),
                ],
            )
            children.append(new_element)
    return children

@app.callback(
    [Output({"type": "dynamic-output", "index": MATCH}, "figure"),
    Output({"type": "dynamic-drop-x", "index": MATCH}, "options"),
    Output({"type": "dynamic-drop-y1", "index": MATCH}, "options"),
    Output({"type": "dynamic-drop-y2", "index": MATCH}, "options")],
    [
        Input({"type": "dynamic-drop-x", "index": MATCH}, "value"),
        Input({"type": "dynamic-drop-x", "index": MATCH}, "options"),
        Input({"type": "dynamic-drop-y1", "index": MATCH}, "value"),
        Input({"type": "dynamic-drop-y1", "index": MATCH}, "options"),
        Input({"type": "dynamic-drop-y2", "index": MATCH}, "value"),
        Input({"type": "dynamic-drop-y2", "index": MATCH}, "options"),
        Input("dpd-well-list", "value"),
        Input("dpd-query-list", "value"),
        Input({"type": "dynamic-color-picker-y1", "index": MATCH}, "value"),
        Input({"type": "dynamic-color-picker-y2", "index": MATCH}, "value"),
    ],
)
def display_output(column_name_x, column_name_x_options, column_name_y1, column_name_y1_options, column_name_y2, column_name_y2_options, well, file_name, color_y1, color_y2):
    con = sqlite3.connect(archivo)
    query=''
    options_x = column_name_x_options
    options_y1 = column_name_y1_options
    options_y2 = column_name_y2_options
    if file_name is not None:
        with open(os.path.join(QUERY_DIRECTORY, file_name)) as f:
            contenido = f.readlines()
        if contenido is not None:
            for linea in contenido:
                query +=  linea 

            df =pd.read_sql(query, con)
            options_x=[{'label': i, 'value': i} for i in df.columns]
            options_y=[{'label': i, 'value': i} for i in df.columns]

        if column_name_y1 not in df.columns:
            column_name_y1 = df.columns[3]
        if column_name_y2 not in df.columns:
            column_name_y2 = df.columns[3]
        if column_name_x not in df.columns:
            column_name_x = df.columns[4]
    return create_figure(column_name_x, column_name_y1, column_name_y2, well, file_name, color_y1, color_y2), options_x, options_y1, options_y2
