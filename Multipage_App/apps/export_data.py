import dash_table
import configparser
import dash_html_components as html
import sqlite3
import os.path
import os
import json
import pandas as pd
from os import listdir
from os.path import isfile, join
import dash_daq as daq
import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Row import Row
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from datetime import datetime, tzinfo, timezone, timedelta, date
from dash_table.Format import Format, Symbol
import dash_admin_components as dac

from app import app 

#Lee el archivo de configuracion
configuracion = configparser.ConfigParser()

#Variable con la ruta para salvar los querys
QUERY_DIRECTORY = "./querys"
CHART_DIRECTORY = "./template/"
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

#Listado de tablas dentro de la BD
cursor = con.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables_list = pd.DataFrame (cursor.fetchall(), columns = ['name'])

#Listado de query
pathway = './querys'
files = [f for f in listdir(pathway) if isfile(join(pathway, f))]
file_list = pd.DataFrame(files, columns = ['NOMBRE'])

layout = html.Div([
    dbc.Row([
        html.Label(['Export Datos'],style={'font-weight': 'bold', "text-align": "left"}),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dac.Box([
                    dac.BoxHeader(
                        collapsible = False,
                        closable = False,
                        title="Tablas de Datos"
                    ),
                    dac.BoxBody([
                        dash_table.DataTable(id="dt_tables_data", 
                            style_as_list_view=True,
                            columns = [{'name': i, 'id': i,} for i in tables_list.columns],
                            data = tables_list.to_dict('records'),
                            style_header={
                                'backgroundColor': 'blue',
                                'fontWeight': 'bold',
                                'color': 'white'
                            },
                            sort_action="native",
                            sort_mode="multi",
                            row_selectable="single",
                            row_deletable=False,
                            selected_columns=[],
                            selected_rows=[],
                            page_current= 0,
                            page_size= 13,
                            style_table={'height': '500px', 'overflowY': 'auto'},
                            style_cell={'textAlign': 'left', 'minWidth': '100px', 'width': '200px', 'maxWidth': '300px'},
                        )
                    ]),	
                ],
                color='primary',
                solid_header=True,
                elevation=4,
                width=12
            ),
        ], width={"size": 5, "offset": 0}),
        dbc.Col([
            dac.Box([
                    dac.BoxHeader(
                        collapsible = False,
                        closable = False,
                        title="Exportar"
                    ),
                    dac.BoxBody([
                        dbc.Row([
                            dbc.Col([
                                html.Label(['Seleccione el Formato :'],style={'font-weight': 'bold', "text-align": "left"}),
                                dcc.RadioItems(id='rb-format-export',
                                    options=[
                                        {'label': '  CSV', 'value': 'CSV'},
                                        {'label': '  Json', 'value': 'JSON'},
                                        {'label': '  EXCEL', 'value': 'EXCEL'}
                                    ],
                                    value='CSV'
                                ),
                            ], width={"size": 5, "offset": 3})
                        ]),
                        html.Br(),
                        daq.ToggleSwitch(
                                id='ts-date-filter',
                                value=False,
                                label='Filtrar tablas por fechas',
                                labelPosition='top'
                            ),
                        dbc.Row([
                            dbc.Col([
                                dcc.DatePickerRange(
                                    id='dtp_fecha',
                                    min_date_allowed= date(1995, 8, 5),
                                    max_date_allowed=date.today(),
                                    start_date = date.today()- timedelta(days=-7),
                                    end_date=date.today(),
                                    display_format='YYYY-MM-DD',
                                    style={'backgroundColor':'white'},
                                ),
                            ], width={"size": 7, "offset": 3}),
                        ]),
                        html.Br(),
                        dbc.Row(
                            dbc.Col(
                                dbc.Button("Exportar", id="btn_export_data", color="success", className="mr-3"),
                                width={"size": 2, "offset": 5}
                            ),
                        ),
                        html.Br(),
                        dbc.Row([
                            dbc.Spinner(
                                html.Div(id="save_export_message")
                            ),
                        ]),
                    ]),	
                ],
                color='primary',
                solid_header=True,
                elevation=4,
                width=12
            ),
        ], width={"size": 4, "offset": 0}),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dac.Box([
                    dac.BoxHeader(
                        collapsible = False,
                        closable = False,
                        title="Consultas"
                    ),
                    dac.BoxBody([
                        dash_table.DataTable(id="dt_querys", 
                            style_as_list_view=True,
                            columns = [{'name': i, 'id': i,} for i in file_list.columns],
                            data = file_list.to_dict('records'),
                            style_header={
                                'backgroundColor': 'blue',
                                'fontWeight': 'bold',
                                'color': 'white'
                            },
                            sort_action="native",
                            sort_mode="multi",
                            row_selectable="single",
                            row_deletable=False,
                            selected_columns=[],
                            selected_rows=[],
                            page_current= 0,
                            page_size= 13,
                            style_table={'height': '500px', 'overflowY': 'auto'},
                            style_cell={'textAlign': 'left', 'minWidth': '100px', 'width': '200px', 'maxWidth': '300px'},
                        )
                    ]),	
                ],
                color='primary',
                solid_header=True,
                elevation=4,
                width=12
            ),
        ], width={"size": 5, "offset": 0}),
    ]),
    html.Br(),
    html.Br(),

])

@app.callback(
    Output("save_export_message", "children"),
    Input("btn_export_data", "n_clicks"),
    Input("dt_tables_data", "data"),
    Input("dt_tables_data", "derived_virtual_selected_rows"),
    Input("dt_querys", "data"),
    Input("dt_querys", "derived_virtual_selected_rows"),
    Input("rb-format-export", "value"),
    Input('ts-date-filter', 'value'), 
    Input('dtp_fecha', 'start_date'),
    Input('dtp_fecha', 'end_date'),
)
def fupdate_table(n_clicks, table_data, table_id, query_data, query_id, formato, filter,dtp_start_date, dtp_end_date, ):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    mensaje = ''
    query=''
    fecha_inicio = str(dtp_start_date)
    fecha_fin = str(dtp_end_date)
    if 'btn_export_data' in changed_id:
        con = sqlite3.connect(archivo)
        if table_id is not None:
            for row_id in table_id:
                table_name =  table_data[row_id]['name']
                query = "SELECT * FROM "+table_name
                if filter:
                    query += " WHERE date(FECHA)>='"+fecha_inicio+"' AND  date(FECHA)<='"+fecha_fin+"' ORDER BY FECHA"
                
                df =pd.read_sql(query, con)
                if formato == 'EXCEL': df.to_excel(EXPORT_DIRECTORY+table_name+".xlsx") 
                if formato == 'CSV': df.to_csv(EXPORT_DIRECTORY+table_name+".csv", index=False) 
                if formato == 'JSON': df.to_json (EXPORT_DIRECTORY+table_name+".json")
        if query_id is not None:
            query=''
            for row_id in query_id:
                query_name =  query_data[row_id]['NOMBRE']
                with open(os.path.join(QUERY_DIRECTORY,query_name)) as f:
                    contenido = f.readlines()
                for linea in contenido:
                    query +=  linea
                df =pd.read_sql(query, con)
                if formato == 'EXCEL': df.to_excel(EXPORT_DIRECTORY+query_name+".xlsx") 
                if formato == 'CSV': df.to_csv(EXPORT_DIRECTORY+query_name+".csv") 
                if formato == 'JSON': df.to_json (EXPORT_DIRECTORY+query_name+".json")
        con.close()
        mensaje='Datos guardados'
    return mensaje


if __name__ == '__main__':
    app.run_server(debug=False)