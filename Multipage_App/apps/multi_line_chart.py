import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Row import Row
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ALL, MATCH
from dash_html_components.Br import Br
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
                        dbc.Button("Agregar Grafico", id="btn_add_chart", color="success", className="mr-3"),
                    ]),
                ]),
                html.Br(),
            ]),
        ], width={"size": 6, "offset": 0}),
    ]),
    html.Div(content),
])

def create_figure(column_x, column_y, well, file_name, selected_color):
    color = dict(hex='#0000ff')
    if selected_color=='rojo':
        color = dict(hex='#FF0000')
    if selected_color=='verde':
        color = dict(hex='#008f39')
    
    quer= ''
    con = sqlite3.connect(archivo)
    fig = {}
    if file_name:
        with open(os.path.join(QUERY_DIRECTORY, file_name)) as f:
            contenido = f.readlines()
            for linea in contenido:
                query =  linea +" ORDER BY FECHA"
            df =pd.read_sql(query, con)
            df = df.query("NOMBRE == '{}'".format(well))
        con.close()
        fig = px.line(df, x=column_x, y=column_y)
        fig.update_layout(
                title="{} {} vs {}".format(well, column_x, column_y),
                margin_l=0,
                margin_r=0,
                margin_b=30,
                hovermode='x unified',
                width=1200,
                height=440,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgb(240, 240, 240)',
            )
        fig.update_traces(line_color=color["hex"]) 
        fig.update_xaxes(title_text="",showline=True, linewidth=2, linecolor='black', showgrid=False,)
        fig.update_yaxes(title_text="",showline=True, linewidth=2, linecolor='black', showgrid=False,)
    return fig

@app.callback(
    Output("container", "children"),
    [
        Input("btn_add_chart", "n_clicks"),
        Input({"type": "dynamic-delete", "index": ALL}, "n_clicks"),
        Input("dpd-well-list", "value"),
        Input("dpd-query-list", "value"),
    ],
    [State("container", "children")],
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
    if 'btn_add_chart' in input_id:
        default_column_x = "FECHA" 
        default_column_y = ""
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
        default_column_y = column_name_list[3]
        default_color = 'Azul'
        
        new_element = html.Div([
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(
                            id={"type": "dynamic-output", "index": n_clicks},
                            style={"height": 440, "width":800},
                            #figure=create_figure(default_column_x, default_column_y, well, file_name, default_color),
                            figure={}
                        ),
                    ], width={"size": 5, "offset": 0}),
                    
                    dbc.Col([
                        html.Div(
                            dbc.Button("Borrar", id={"type": "dynamic-delete", "index": n_clicks}, n_clicks=0, color="warning", className="mr-3"),
                            className="d-grid gap-2 d-md-flex justify-content-md-end"
                        ),
                        html.Label(['Eje X:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                            id={"type": "dynamic-dropdown-x", "index": n_clicks},
                            options=[{"label": i, "value": i} for i in df.columns],
                            value=default_column_x,
                            clearable=False,
                        ), 
                        html.Label(['Eje Y:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                            id={"type": "dynamic-dropdown-y", "index": n_clicks},
                            options=[{"label": i, "value": i} for i in df.columns],
                            value=default_column_y,
                            clearable=False,
                        ),
                        html.Label(['Color Linea:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                            id={"type": "dynamic-color-picker", "index": n_clicks},
                            options=[
                                {'label': 'Azul', 'value': 'azul'},
                                {'label': 'Rojo', 'value': 'rojo'},
                                {'label': 'Verde', 'value': 'verde'}
                            ],
                            value='azul',
                        ),
                    ], width={"size": 3, "offset": 3}),
                ]),
            ],
        )
        children.append(new_element)
    return children

@app.callback(
    Output({"type": "dynamic-output", "index": MATCH}, "figure"),
    [
        Input({"type": "dynamic-dropdown-x", "index": MATCH}, "value"),
        Input({"type": "dynamic-dropdown-y", "index": MATCH}, "value"),
        Input("dpd-well-list", "value"),
        Input("dpd-query-list", "value"),
        Input({"type": "dynamic-color-picker", "index": MATCH}, "value"),
    ],
)
def display_output(column_name_x, column_name_y, well,file_name, color):
    return create_figure(column_name_x, column_name_y, well, file_name, color)
