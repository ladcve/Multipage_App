import dash_tabulator
import dash
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
from textwrap import dedent as d
import json
from os import listdir
from os.path import isfile, join
import sqlite3
import configparser
import sys
import os.path
import os
import pandas as pd
from datetime import date

# 3rd party js to export as xlsx
external_scripts = ['https://oss.sheetjs.com/sheetjs/xlsx.full.min.js']

# bootstrap css
external_stylesheets = ['https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css']

# initialize your dash app as normal
app = dash.Dash(__name__, external_scripts=external_scripts, external_stylesheets=external_stylesheets)

styles = {
            'pre': {
                'border': 'thin lightgrey solid',
                'overflowX': 'scroll'
            }
        }

#Variable con la ruta para salvar los querys
QUERY_DIRECTORY = "./querys"
CHART_DIRECTORY = "./template/"

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
query = ''
data = pd.DataFrame()

with open(os.path.join(QUERY_DIRECTORY, 'data_asignada_lectura_dashboard.sql')) as f:
    contenido = f.readlines()
    if contenido is not None:
        for linea in contenido:
            query +=  linea
        query += " AND A.FECHA = '2021-08-01 00:00:00'"
        data =pd.read_sql(query, con)
con.close()

columns = [
            { "title": "NOMBRE", "field": "NOMBRE", "width": 100},
            { "title": "TASA_GAS", "field": "TASA_GAS", "hozAlign": "left", "formatter": "progress" },
            { "title": "TASA_CONDENSADO", "field": "TASA_CONDENSADO",  "hozAlign": "left" },
            { "title": "TASA_AGUA", "field": "TASA_AGUA", "hozAlign": "left" },
            { "title": "PRESION_CABEZAL", "field": "PRESION_CABEZAL", "width": 100},
            { "title": "PRESION_FONDO_A", "field": "PRESION_FONDO_A", "hozAlign": "left"},
            { "title": "PRESION_FONDO_B", "field": "PRESION_FONDO_B",  "hozAlign": "left" },
            { "title": "CHOKE", "field": "CHOKE", "hozAlign": "left" },
            { "title": "PRESION_LINEA", "field": "PRESION_LINEA", "hozAlign": "left" },
]


#columns = [{'label': i, 'value': i, "hozAlign": "left", "formatter": "progress"} for i in data.columns]

data = data.to_dict('records')

print(columns)
print(data)
# Additional options can be setup here 
# these are passed directly to tabulator
# In this example we are enabling selection
# Allowing you to select only 1 row
# and grouping by the col (color) column 

options = { "groupBy": "col", "selectable":1}

# downloadButtonType
# takes 
#       css     => class names
#       text    => Text on the button
#       type    => type of download (csv/ xlsx / pdf, remember to include appropriate 3rd party js libraries)
#       filename => filename prefix defaults to data, will download as filename.type

downloadButtonType = {"css": "btn btn-primary", "text":"Export", "type":"xlsx"}

app.layout = html.Div([
    dash_tabulator.DashTabulator(
        id='tabulator',
        columns=columns,
        data=data,
        options=options,
        downloadButtonType=downloadButtonType,
    ),
])

if __name__ == '__main__':
    app.run_server(debug=False)