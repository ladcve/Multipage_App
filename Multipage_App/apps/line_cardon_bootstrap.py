from datetime import date
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
from pandas.core.indexes import multi
import plotly.express as px
import pyodbc 
import pandas as pd
from app import app

conexion = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=SVPTG01PMS91\MSSQLSERVER_PMS' + 
';DATABASE=PDMS;UID=pdmsadm;PWD=Card0n2021$06')

wells = pd.read_sql_query("SELECT NOMBRE FROM ITEMS WHERE TIPO='POZO' AND ESTATUS=1",conexion)
wells = wells.sort_values('NOMBRE')['NOMBRE'].unique()

targetviews = pd.read_sql_query("SELECT name FROM sysobjects  WHERE xtype = 'V' and name like '%_POZO'",conexion)
vistas = targetviews.sort_values('name')['name'].unique()

atributos = pd.read_sql_query("SELECT COLUMN_NAME, TABLE_NAME FROM INFORMATION_SCHEMA.COLUMNS  WHERE  COLUMN_NAME NOT IN  ('ITEMID','NOMBRE', 'FLUIDO','FUNCION', 'FECHA', 'RAZON')",conexion)

layout = html.Div(
    [
    dbc.Row(
        dbc.Col(
            html.Div([
                html.Label(['Pozos:'],style={'font-weight': 'bold', "text-align": "left"}),
                dcc.Dropdown(
                    id='pozos-dropdown', value='Perla-1x', clearable=False,
                    persistence=True, persistence_type='session',
                    options=[{"label": x, "value": x} for x in wells],
                    style={'height': '25px', 'width':'110px', 'display': 'inline-block', 'font-size': '8'}
                ),
            ]))),
    html.Hr( style={"border-top": "2px solid black"}),
    dbc.Row([
        dbc.Col([
            html.Div(dcc.Graph(id='line-chart')),
        ],width={'size':10, 'offset':0, 'order':1}),

        dbc.Col([
            dbc.Row(html.Label(['Fuentes:'],style={'font-weight': 'bold', "text-align": "left"})),
            dbc.Row([
                dcc.Dropdown(
                    id='vistas-dropdown', value='ESTIMACIONES_POZO', clearable=False,
                    persistence=True, persistence_type='local',
                    options=[{"label": x, "value": x} for x in vistas],
                    style={'height': '25px', 'width':'200px', 'display': 'inline-block', 'font-size': '8'}
                ),
            ]),
            dbc.Row(html.Label(['Atributos:'],style={'font-weight': 'bold', "text-align": "left"})),
            dbc.Row([
                dcc.Dropdown(
                    id='atributos-dropdown', clearable=False,
                    persistence=True, persistence_type='local', multi='True',
                    style={'height': '200px', 'width':'200px', 'display': 'inline-block', 'font-size': '8'}
                )
            ])
        ], width={'size':2, 'offset':0, 'order':2}),
    ]),
])

@app.callback(
    dash.dependencies.Output('atributos-dropdown', 'options'),
    [dash.dependencies.Input('vistas-dropdown', 'value')])
def set_cities_options(vista):
    columns_names=atributos[atributos['TABLE_NAME']==vista]['COLUMN_NAME']
    columns_names_list = list(columns_names)
    return [{"label": x, "value": x} for x in columns_names_list]

@app.callback(
    dash.dependencies.Output('atributos-dropdown', 'value'),
    [dash.dependencies.Input('atributos-dropdown', 'options')])
def set_cities_value(available_options):
    return available_options[0]['value']

@app.callback(
    dash.dependencies.Output('line-chart','figure'),
    [dash.dependencies.Input('pozos-dropdown', 'value'),
     dash.dependencies.Input('vistas-dropdown', 'value')
     ])
def update_line_chart(pozo, vista):
    #dff=datos[(datos['NOMBRE']==pozo)]
    #cadena = ",".join(atributo_lista)
    dff = pd.read_sql_query("SELECT * FROM "+vista+" WHERE NOMBRE='"+pozo+"' ORDER BY FECHA",conexion)
    columns_names = dff.columns.values
    columns_names_list = list(columns_names)
    print (dff)
    fig = px.line(dff, x="FECHA", y=columns_names_list[5:])
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
    return fig