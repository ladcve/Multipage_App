import dash
from dash.dependencies import Input, Output, State, ALL, MATCH
import dash_html_components as html
import dash_core_components as dcc
import plotly.express as px
from os import listdir
from os.path import isfile, join
import sqlite3
import configparser
import sys
import os.path
import os
import pandas as pd
import json
from datetime import date

app = dash.Dash(__name__)

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

query = "SELECT NOMBRE FROM VARIABLES"
var_list =pd.read_sql(query, con)
var_list = var_list.sort_values('NOMBRE')['NOMBRE'].unique()

#Listado de eventos
query = "SELECT * FROM CIERRE_DIARIO_POZO"
df =pd.read_sql(query, con)
df = df.sort_values(by=['NOMBRE', 'FECHA'])

con.close()

app.layout = html.Div(
    [
        html.Div(
            children=[
                html.Button(
                    "Add Chart",
                    id="add-chart",
                    n_clicks=0,
                    style={"display": "inline-block"},
                ),
                dcc.Checklist(
                    id="cb_clear_data",
                    options=[{"label": "Eliminar Ceros", "value": "YES"}],
                    value=[],
                    labelStyle={"display": "inline-block"},
                ),
            ]
        ),
        html.Div(id="container", children=[]),
    ]
)


def create_figure(well, column_y, clear_data):
    chart_type = px.line 
    dff = pd.DataFrame()
    dff = df
    if clear_data:
        dff = dff.loc[dff[column_y] >0]
    return (
        chart_type(dff.query("NOMBRE == '{}'".format(well)), x='FECHA', y=column_y,)
        .update_layout(
            title="{} {}".format(well, column_y),
            margin_l=10,
            margin_r=0,
            margin_b=30,
        )
        .update_xaxes(title_text="")
        .update_yaxes(title_text="")
        .update_xaxes(
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
    )


@app.callback(
    Output("container", "children"),
    [
        Input("add-chart", "n_clicks"),
        Input({"type": "dynamic-delete", "index": ALL}, "n_clicks"),
        Input("cb_clear_data", "value"),
    ],
    [State("container", "children")],
)
def display_dropdowns(n_clicks, _, clear_data, children,):
    default_well = well_list[0]
    default_column_y = df.columns[3]

    input_id = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
    if "index" in input_id:
        delete_chart = json.loads(input_id)["index"]
        children = [
            chart
            for chart in children
            if "'index': " + str(delete_chart) not in str(chart)
        ]
    else:
        new_element = html.Div(
            style={
                "width": "23%",
                "display": "inline-block",
                "outline": "thin lightgrey solid",
                "padding": 10,
            },
            children=[
                html.Button(
                    "X",
                    id={"type": "dynamic-delete", "index": n_clicks},
                    n_clicks=0,
                    style={"display": "block"},
                ),
                dcc.Graph(
                    id={"type": "dynamic-output", "index": n_clicks},
                    style={"height": 300},
                    figure=create_figure(default_well, default_column_y, clear_data),
                ),
                dcc.Dropdown(
                    id={"type": "dynamic-well", "index": n_clicks},
                    options=[{"label": i, "value": i} for i in well_list],
                    value=default_well,
                ),
                dcc.Dropdown(
                    id={"type": "dynamic-dropdown-y", "index": n_clicks},
                    options=[{"label": i, "value": i} for i in df.columns],
                    value=default_column_y,
                ),
            ],
        )
        children.append(new_element)
    return children


@app.callback(
    Output({"type": "dynamic-output", "index": MATCH}, "figure"),
    [
        Input({"type": "dynamic-well", "index": MATCH}, "value"),
        Input({"type": "dynamic-dropdown-y", "index": MATCH}, "value"),
        Input("cb_clear_data", "value"),
    ],
)
def display_output(well, column_y, clear_data):
    return create_figure(well, column_y, clear_data)


if __name__ == "__main__":
    app.run_server(debug=False)