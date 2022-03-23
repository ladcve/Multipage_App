import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Row import Row
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ALL, MATCH
import dash_admin_components as dac
import base64
import plotly.express as px
import plotly.graph_objects as go
from os import listdir
from os.path import isfile, join
import sqlite3
import configparser
import sys
import os.path
import json
import os
import pandas as pd
from datetime import datetime, tzinfo, timezone, timedelta, date
import dash_table

from app import app 

#Variable con la ruta para salvar los querys
QUERY_DIRECTORY = "./querys"
CHART_DIRECTORY = "./template/"
PICTURE_DIRECTORY = "./pictures/"


#Define el nombre de las imagenes que mostraran en el dashboard
gas_png = PICTURE_DIRECTORY+'gas.png'
cond_png = PICTURE_DIRECTORY+'condensado.png'
wat_png = PICTURE_DIRECTORY+'water.png'
perd_png = PICTURE_DIRECTORY+'perdidas.png'
pot_png = PICTURE_DIRECTORY+'potencial.png'
press_png = PICTURE_DIRECTORY+'pressure.png'
temp_png = PICTURE_DIRECTORY+'ptermometro.png'
choke_png = PICTURE_DIRECTORY+'choke.png'

gas_base64 = base64.b64encode(open(gas_png, 'rb').read()).decode('ascii')
cond_base64 = base64.b64encode(open(cond_png, 'rb').read()).decode('ascii')
wat_base64 = base64.b64encode(open(wat_png, 'rb').read()).decode('ascii')
perd_base64 = base64.b64encode(open(perd_png, 'rb').read()).decode('ascii')
pot_base64 = base64.b64encode(open(pot_png, 'rb').read()).decode('ascii')
press_base64 = base64.b64encode(open(press_png, 'rb').read()).decode('ascii')
temp_base64 = base64.b64encode(open(temp_png, 'rb').read()).decode('ascii')
choke_base64 = base64.b64encode(open(choke_png, 'rb').read()).decode('ascii')

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


#Listado de unidades por variables
query = "SELECT * FROM UNIDADES"
unidades =pd.read_sql(query, con)

con.close()

#Listado de query
pathway = './querys'
files = [f for f in listdir(pathway) if isfile(join(pathway, f))]

file_name = ''
df = pd.DataFrame()

#**** Cabecera de la pagina
cabecera = dac.TabItem(id='content_value_boxes',             
    children=[
        dbc.Row([
            dbc.Col([
                dac.InfoBox(
                    id='ind-prodgas',
                    title = "Gas Producido",
                    color = "success",
                    icon = "burn",
                    width = 12,
                    ),
            ], width={"size": 2, "offset": 0}),
            dbc.Col([
                dac.InfoBox(
                    id='ind-prodcond',
                    title = "Condensado Producido",
                    color = "success",
                    icon = "oil-can",
                    width = 12
                    ),
            ], width={"size": 2, "offset": 0}),
            dbc.Col([
                dac.InfoBox(
                    id='ind-prodwat',
                    title = "Agua Producida",
                    color = "success",
                    icon = "water",
                    style={'font_Size': '30px', 'font-family':'arial'},
                    width = 12
                    ),
            ], width={"size": 2, "offset": 0}),
            dbc.Col([
                dac.InfoBox(
                    id='ind-perdidas',
                    title = "Perdidas (diferida alta)",
                    color = "success",
                    icon = "level-down-alt",
                    width = 12
                    ),
            ], width={"size": 2, "offset": 0}),
            dbc.Col([
                dac.InfoBox(
                    id='ind-potencial',
                    title = "Potencial",
                    color = "success",
                    icon = "chart-line",
                    width = 12
                    ),
            ], width={"size": 2, "offset": 0}),
        ]),
    ]
)

layout = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.Row([
                    dbc.Col([
                        html.Label(['Fecha: '],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.DatePickerSingle(
                            id='dtp_fecha_dashboard',
                            date=pd.to_datetime("today"),
                            display_format='YYYY-MM-DD',
                            style={'backgroundColor':'white'},
                        )
                    ], width={"size": 2, "offset": 1}),
                    dbc.Col([
                        html.Label(['Consulta:'],style={'font-weight': 'bold', "text-align": "left"}),
                        dcc.Dropdown(
                            id='dpd-consulta-lista',
                            options=[
                                {'label': i, 'value': i} for i in files
                            ],
                            clearable=False,
                            multi=False,
                        ),
                    ], width={"size": 4, "offset": 0}),
                    dbc.Col([
                        html.Br(),
                        dbc.Button(html.Span(["Mostrar ", html.I(className="fas fa-tv ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                         id="btn_show_data", n_clicks=0, color="success", className="mr-3"),
                    ]),
                    dbc.Col([
                        html.Br(),
                        dbc.Button(html.Span(["Agregar ", html.I(className="fas fa-chart-bar ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                         id="btn_add_chart", n_clicks=0, color="success", className="mr-3"),
                    ]),
                    dbc.Col([
                        html.Br(),
                        dcc.Checklist(
                            id="cb_clear_data",
                            options=[{"label": "  Limpiar valores Ceros", "value": "YES"}],
                            value=[],
                            labelStyle={"display": "inline-block"},
                        ),
                    ])
                ]),
                html.Br(),
            ], style={"background-color": "#F9FCFC"}),
        ], width={"size": 11, "offset": 0}),
    ]),
    html.Br(),
    cabecera,
    html.Br(),
    dbc.Row([
        dbc.Col([
            dac.Box(
                [
                    dac.BoxHeader(
                        collapsible = False,
                        closable = False,
                        title="Comparativa"
                    ),
                	dac.BoxBody(
                        dcc.Loading(
                            dash_table.DataTable(id="dt_compare_results",        
                                style_as_list_view=True,
                                style_cell={'padding': '5px', 'fontSize':15, 'font-family':'arial'},
                                style_header={
                                    'backgroundColor': 'blue',
                                    'fontWeight': 'bold',
                                    'color': 'white',
                                    'font-family':'arial'
                                },
                                style_table={'overflowX': 'auto'},
                                editable=False,),
                            )	
                    ),
                ],
                color='primary',
                solid_header=True,
                elevation=4,
                width=12
            ),
        ], width=12),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dac.Box(
                [
                    dac.BoxHeader(
                        collapsible = True,
                        closable = True,
                        title="Graficos de Tendencia"
                    ),
                	dac.BoxBody(
                        dcc.Loading(
                            html.Div(id="chart_container", children=[]),
                        ),
                    )		
                ],
                color='primary',
                solid_header=True,
                elevation=4,
                width=12
            ),
        ], width=12),
    ]),
])

def create_figure(well, column_y, clear_data, file_name, chart_type):

    con = sqlite3.connect(archivo)
    fig = {}
    query=''
    if file_name:
        with open(os.path.join(QUERY_DIRECTORY, file_name)) as f:
            contenido = f.readlines()
        if contenido is not None:
            for linea in contenido:
                query +=  linea 

            df =pd.read_sql(query, con)
            df = df.sort_values(by=['FECHA'])

        if clear_data:
            df = df.loc[df[column_y] >0]

        selec_unit = unidades.set_index(['VARIABLE'])
        var_title = selec_unit.loc[column_y]['GRAFICO']
        var_unit = selec_unit.loc[column_y]['UNIDAD']
        var_color = selec_unit.loc[column_y]['COLOR']
        var_name = var_title + " " + var_unit

        color = dict(hex=var_color)

        #df = df.set_index('NOMBRE')
        if chart_type == 'LINE':
            #fig = px.line(df.query("NOMBRE in '{}'".format(well)), x='FECHA', y=column_y)
            fig = px.line(df[df['NOMBRE'].isin(well)], x='FECHA', y=column_y)
        if chart_type == 'BAR':
            fig = px.bar(df[df['NOMBRE'].isin(well)], x='FECHA', y=column_y)
        if chart_type == 'AREA':
            fig = px.area(df[df['NOMBRE'].isin(well)], x='FECHA', y=column_y)
        if chart_type == 'PIE':
            if well is not None:
                df= df[df['NOMBRE'].isin(well)]

            df3 = pd.DataFrame()
            filtro = ['NOMBRE']
            filtro.append(column_y)
            df2 = df[filtro]
            df2.rename(columns={column_y: "VOLUMEN"}, inplace=True)
            df2['FLUIDO']=column_y
            df3 = df3.append(df2)

            if len(df)>0:
                fig =px.sunburst(
                        df3,
                        path=['NOMBRE', 'FLUIDO'],
                        height=300,
                        values='VOLUMEN',
                    )

        if chart_type == 'AREA' or chart_type == 'LINE':
            fig.update_layout(
                title="{} {}".format(well, var_name),
                hovermode='x unified',
                margin_l=10,
                margin_r=0,
                margin_b=30,
            )
            fig.update_traces(line_color=color["hex"])
            fig.update_xaxes(title_text="")
            fig.update_yaxes(title_text="")
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
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
    return fig


@app.callback(
    Output("chart_container", "children"),
    [
        Input("btn_add_chart", "n_clicks"),
        Input({"type": "dynamic-delete-chart", "index": ALL}, "n_clicks"),
    ],
    [State("cb_clear_data", "value"), State("dpd-consulta-lista", "value"), State("chart_container", "children")],
)
def display_dropdowns(n_clicks, _, clear_data, file_name,  children):

    input_id = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
    if "index" in input_id:
        delete_chart = json.loads(input_id)["index"]
        children = [
            chart
            for chart in children
            if "'index': " + str(delete_chart) not in str(chart)
        ]
    else:
        con = sqlite3.connect(archivo)
        default_column_y = ''
        query=''
        if file_name:
            with open(os.path.join(QUERY_DIRECTORY, file_name)) as f:
                contenido = f.readlines()
            if contenido is not None:
                for linea in contenido:
                    query +=  linea 

                df =pd.read_sql(query, con)
                df.reset_index(drop=True, inplace=True)

                if  df.columns[2]=='FECHA':
                    default_column_y = df.columns[3]
                else:
                    default_column_y = df.columns[2]

            default_well = [well_list[0]]
            new_element = html.Div(
                style={
                    "width": "33%",
                    "display": "inline-block",
                    "outline": "thin lightgrey solid",
                    "padding": 10,
                },
                children=[
                    dbc.Row([
                        dbc.Col([
                            html.Label(['Tipo de Gráfico'],style={'font-weight': 'bold', "text-align": "left"}),
                            dcc.Dropdown(
                                id={"type": "dynamic-chart-type", "index": n_clicks},
                                options=[
                                    {'label': 'Línea', 'value': 'LINE'},
                                    {'label': 'Barra', 'value': 'BAR'},
                                    {'label': 'Área', 'value': 'AREA'},
                                    {'label': 'Torta', 'value': 'PIE'},
                                ],
                                value='LINE',
                            ),
                        ]),
                        dbc.Col([
                            html.Div([
                                dbc.Button(html.Span([ html.I(className="fas fa-trash-alt ml-1")],style={'font-size':'1.5em','text-align':'center'}),
                                    id={"type": "dynamic-delete-chart", "index": n_clicks},
                                    n_clicks=0,
                                    style={"display": "block"},
                                    color="danger", className="mr-1"),
                            ], className="d-grid gap-2 d-md-flex justify-content-md-end",),
                        ]),
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(
                                id={"type": "dynamic-chart-output", "index": n_clicks},
                                style={"height": 300},
                                #figure=create_figure(default_well, default_column_y, color, clear_data, file_name),
                                figure={}
                            ),
                            dcc.Dropdown(
                                id={"type": "dynamic-well", "index": n_clicks},
                                options=[{"label": i, "value": i} for i in well_list],
                                value=default_well,
                                multi=True,
                            ),
                            dcc.Dropdown(
                                id={"type": "dynamic-dropdown-y", "index": n_clicks},
                                options=[{"label": i, "value": i} for i in df.columns],
                                value=default_column_y,
                                multi=False, 
                            ),
                        ]),
                    ]),
                ],
            )
            children.append(new_element)
    return children


@app.callback(
    [Output({"type": "dynamic-chart-output", "index": MATCH}, "figure"),
    Output({"type": "dynamic-dropdown-y", "index": MATCH}, "options")],
    [
        Input({"type": "dynamic-well", "index": MATCH}, "value"),
        Input({"type": "dynamic-dropdown-y", "index": MATCH}, "value"),
        Input({"type": "dynamic-dropdown-y", "index": MATCH}, "options"),
        Input("cb_clear_data", "value"),
        Input("dpd-consulta-lista", "value"),
        Input({"type": "dynamic-chart-type", "index": MATCH}, "value"),
    ],
)
def display_output(well, column_y, y_options, clear_data, file_name, chart_type):
    con = sqlite3.connect(archivo)
    query=''
    options = y_options
    if file_name is not None:
        with open(os.path.join(QUERY_DIRECTORY, file_name)) as f:
            contenido = f.readlines()
        if contenido is not None:
            for linea in contenido:
                query +=  linea 

            #Filtrar solo la primera fila para obtener los nombre de column
            query += " LIMIT 1"

            df =pd.read_sql(query, con)
            if  df.columns[2]=='FECHA':
                options=[{'label': i, 'value': i} for i in df.columns[3:]]
            else:
                options=[{'label': i, 'value': i} for i in df.columns[2:]]

        if column_y not in df.columns:
            if  df.columns[2]=='FECHA':
                column_y = df.columns[3]
            else:
                column_y = df.columns[2]
            
         
    return create_figure(well, column_y, clear_data, file_name, chart_type), options

@app.callback(
    [Output("dt_compare_results", "data"), Output("dt_compare_results", "columns"),
    Output('ind-prodgas', 'value'),
    Output('ind-prodcond', 'value'),
    Output('ind-prodwat', 'value'),
    Output('ind-perdidas', 'value'),
    Output('ind-potencial', 'value')],
    [Input("btn_show_data", "n_clicks"),
    Input("dtp_fecha_dashboard", "date"),
    Input("dpd-consulta-lista", "value")]
)
def update_table_compare(n_clicks, report_date, file_name):
    df = pd.DataFrame()
    query= ''
    con = sqlite3.connect(archivo)
    filter = True
    
    cursor = con.execute("SELECT ROUND(SUM(TASA_GAS),6) FROM CIERRE_DIARIO_POZO WHERE FECHA='"+report_date+" 00:00:00'")
    valor= cursor.fetchall()
    if valor:
        for data in valor:
            if data[0] is None:
                valor_prodgas = ' {} MMPCD'.format(0)
            else:
                valor_prodgas = ' {} MMPCD'.format(data[0])
    else:
        valor_prodgas = ""
    
    cursor = con.execute("SELECT ROUND(SUM(TASA_CONDENSADO),2) FROM CIERRE_DIARIO_POZO WHERE FECHA='"+report_date+" 00:00:00'")
    valor= cursor.fetchall()
    if valor:
        for data in valor:
            if data[0] is None:
                valor_prodcond = ' {} BLS'.format(0)
            else:
                valor_prodcond = ' {} BLS'.format(data[0])
    else:
        valor_prodcond = ""
    
    cursor = con.execute("SELECT ROUND(SUM(TASA_AGUA),2) FROM CIERRE_DIARIO_POZO WHERE FECHA='"+report_date+" 00:00:00'")
    valor= cursor.fetchall()
    if valor:
        for data in valor:
            if data[0] is None:
                valor_prodwat = ' {} BLS'.format(0)
            else:
                valor_prodwat = ' {} BLS'.format(data[0])
    else:
         valor_prodwat = ''

    cursor = con.execute("SELECT ROUND(SUM(DIFERIDA_ALTA_GAS),6) FROM PERDIDAS_POZO WHERE FECHA='"+report_date+" 00:00:00'")
    valor= cursor.fetchall()
    if valor:
        for data in valor:
            if data[0] is None:
                valor_perdidas = ' {} BLS'.format(0)
            else:
                valor_perdidas = ' {} BLS'.format(data[0])
    else:
        valor_perdidas = ""
    
    cursor = con.execute("SELECT ROUND(SUM(VOLUMEN_GAS),6) FROM POTENCIAL_POZO WHERE FECHA = (SELECT MAX(FECHA) FROM POTENCIAL_POZO)")
    valor= cursor.fetchall()

    if valor:
        for data in valor:
            if data[0] is None:
                valor_potencial = ' {} BLS'.format(0)
            else:
                valor_potencial = ' {} BLS'.format(data[0])
    else:
        valor_potencial = ""

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    
    if 'btn_show_data' in changed_id:
        if file_name is not None:
            with open(os.path.join(QUERY_DIRECTORY, file_name)) as f:
                contenido = f.readlines()
            if contenido is not None:
                for linea in contenido:
                    query +=  linea

                df =pd.read_sql(query, con)

                #Busca el index como columna en el dataframe
                #si existe lo borra
                index_cols = [col for col in df.columns if 'index' in col]
                if index_cols:
                    df =df.drop(['index'], axis=1)

                if query.find("PRUEBAS_POZO")>-1 or query.find("POTENCIAL_POZO")>-1:
                    df = df[df['FECHA']<= report_date+" 00:00:00"]
                    df = df.groupby('NOMBRE').nth(-1)
                else:
                    df = df.loc[df['FECHA'] == report_date+" 00:00:00"]

    columns = [{'name': i, 'id': i, "deletable": True} for i in df.columns]
    data = df.to_dict('records')
    
    return data, columns, valor_prodgas, valor_prodcond, valor_prodwat, valor_perdidas, valor_potencial