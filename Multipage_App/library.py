import plotly.graph_objects as go
from plotly.subplots import make_subplots
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
import collections
from calendar import monthrange
import datetime
import os

#Variable con la ruta para salvar los querys
QUERY_DIRECTORY = "./querys"
CHART_DIRECTORY = "./template/"

def search_calcv( archivo, calc_variable):
    #Inicializa las variables
    ecuacion = ''
    titulo = ''
    requisitos=''

    con = sqlite3.connect(archivo)
    query = "SELECT * FROM VARIABLES"
    variables =pd.read_sql(query, con)

    selec_var=variables.loc[variables['NOMBRE']==calc_variable]
    ecuacion = selec_var.iloc[0]['ECUACION']
    requisitos = selec_var.iloc[0]['REQUISITO']
    titulo = selec_var.iloc[0]['TITULO']
    requisitos_list = list(requisitos.split(","))
      
    return requisitos_list, titulo, ecuacion

def search_unit(unidades, variable):
    #Busca las unidades para una variable en especifico
    selec_unit = unidades.set_index(['VARIABLE'])
    var_title = selec_unit.loc[variable]['GRAFICO']
    var_unit = selec_unit.loc[variable]['UNIDAD']
    var_color = selec_unit.loc[variable]['COLOR']
    var_name = var_title + " " + var_unit
    return var_name, var_color

def create_chart(archivo, unidades, file_name, well_name, column_list_y1, column_list_y2, show_annot, annot_data, var_list, color_y1, color_y2, clear_data, stile_y1, stile_y2, anota_color, group_by,agregation_fun, show_rocio, rocio_data):

    color_axis_y1 = dict(hex=color_y1)
    color_axis_y2 = dict(hex=color_y2)
    back_color = dict(hex=anota_color)
    var_color = '#1530E3'
    #var_name = ''

    df = pd.DataFrame()
    query= ''
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    ecuacion = ''
    titulo = ''
    
    con = sqlite3.connect(archivo)

    #Listado de tablas en la BD
    cursor = con.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables_list = pd.DataFrame (cursor.fetchall(), columns = ['name'])
    tables_list = tables_list.sort_values('name')['name'].unique()

    if file_name is not None:
        with open(os.path.join(QUERY_DIRECTORY, file_name)) as f:
            contenido = f.readlines()
        if contenido is not None:
            query = ''
            for linea in contenido:
                query +=  linea 

            df =pd.read_sql(query, con)

            if well_name:
                df = df[df['NOMBRE']==well_name]
                
            df = df.sort_values(by="FECHA")
            
            if clear_data:
                df = df[(df!=0)]

            if group_by:
                if agregation_fun == 'SUM':
                    df =df.groupby('FECHA', as_index=True).sum().reset_index()
                else:
                    df =df.groupby('FECHA', as_index=True).mean().reset_index()

            if var_list:
                for columna in df.columns:
                    if columna != 'FECHA' and columna != 'NOMBRE':
                        df[columna] = pd.to_numeric(df[columna])

                for var in var_list:
                    requisitos_list, titulo, ecuacion = search_calcv( archivo, var)

                    if search_list(requisitos_list, df.columns.tolist()):
                        df[titulo] =eval(ecuacion)
                        var_name = titulo
                    
            i=1

            if column_list_y1:
                for columnas_y1 in column_list_y1:
                    #Valida que la columna seleccionada este en el dataframe
                    if columnas_y1 in df:
                        var_name, var_color = search_unit(unidades, columnas_y1)

                        if color_axis_y1 == {'hex': '#1530E3'} and var_color:
                            color_axis_y1 = dict(hex=var_color)
                                
                        fig.add_trace(
                            go.Scatter(x=df['FECHA'],
                                y=df[columnas_y1],
                                name=var_name,
                                connectgaps=True,
                                line_color=color_axis_y1["hex"],
                                yaxis= 'y'+ str(i),
                                line={'dash': stile_y1},
                                
                            ),
                            #secondary_y=True,
                        )
                    i=+1

            if column_list_y2 :
                for columnas_y2 in column_list_y2:

                    #Valida que la columna seleccionada este en el dataframe
                    if columnas_y1 in df:
                        var_name, var_color = search_unit(unidades, columnas_y2)

                        if color_axis_y2 == {'hex': '#1530E3'}:
                            color_axis_y2 = dict(hex=var_color)

                        fig.add_trace(
                            go.Scatter(x=df['FECHA'],
                                y=df[columnas_y2],
                                name=var_name,
                                connectgaps=True,
                                line_color=color_axis_y2["hex"],
                                yaxis= 'y'+ str(i),
                                line={'dash': stile_y2},
                            ),
                            secondary_y=True,
                        )
                        i=+1
            fig.update_xaxes(title_text="Fecha",showline=True, linewidth=2, linecolor='black', showgrid=False,)
            fig.update_yaxes(showline=True, linewidth=2, linecolor='black', showgrid=False,)
            fig.update_layout(
                autosize=False,
                hovermode='x unified',
                height=700,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgb(240, 240, 240)',
                margin=dict(
                    l=50,
                    r=50,
                    b=100,
                    t=100,
                    pad=4,
                ),
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
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
            if show_annot:
                dff = pd.DataFrame(annot_data)
                for ind in dff.index:
                    fig.add_annotation(x=dff['FECHA'][ind], y=5,
                        text=dff['EVENTO'][ind],
                        showarrow=False,
                        bgcolor=back_color["hex"],
                        textangle=-90,
                        arrowhead=1)
            if show_rocio and well_name:
                df_rocio = pd.DataFrame(rocio_data)
                df_rocio = df_rocio[df_rocio['NOMBRE']==well_name]
                fig.add_hline(y=df_rocio['PRESION'].iloc[0],
                    line_color="green",
                    line_dash="dot",
                    annotation_text="Presion Rocio", 
                    annotation_position="bottom left"
                )
    con.close()

    return fig

def create_chart_single(archivo, unidades, file_name, well_name, column_data, clear_data, min_val, max_val):

    df = pd.DataFrame()
    query= ''
    fig = make_subplots()
    var_name = ''
    color_axis = dict(hex='#1530E3')
    
    con = sqlite3.connect(archivo)

    if file_name is not None:
        with open(os.path.join(QUERY_DIRECTORY, file_name)) as f:
            contenido = f.readlines()
        if contenido is not None:
            query = ''
            for linea in contenido:
                query +=  linea 

            df =pd.read_sql(query, con)

            if well_name:
                df = df[df['NOMBRE']==well_name]
                
            df = df.sort_values(by="FECHA")
            
            if clear_data:
                df = df[(df!=0)]

            df['indice'] = np.arange(len(df))

            df= df[(df['indice'] >= min_val) & (df['indice'] <= max_val)]

            if column_data in df.columns:
                fig.add_trace(
                    go.Scatter(x=df['indice'],
                        y=df[column_data],
                        connectgaps=True,
                    ),
                )
                
            fig.update_xaxes(title_text="Fecha",showline=True, linewidth=2, linecolor='black', showgrid=False,)
            fig.update_yaxes(showline=True, linewidth=2, linecolor='black', showgrid=False,)
            fig.update_layout(
                autosize=False,
                hovermode='x unified',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgb(240, 240, 240)',
                margin=dict(
                    l=50,
                    r=50,
                    b=100,
                    t=100,
                    pad=4,
                ),
                )

    con.close()

    return fig

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


def listToString(s): 
    
    # initialize an empty string
    str1 = "" 
    
    # traverse in the string  
    for ele in s: 
        str1 += ele  
    
    # return string  
    return str1 

def reform_df(dft):
    # quick and dirty stacking of cols 2,3 on 0,1
    dfl = dft[[0,1]]
    dfr = dft[[2,3]]
    dfr.columns = 0,1
    dfout = pd.concat([dfl,dfr])
    dfout.columns=['Parameter','Value']
    return dfout

#Seccion de funciones
def prefijo_tabla(tabla):
    prefijo =''
    if tabla=='CIERRE_DIARIO_POZO':
        prefijo='CEP'
    if tabla=='LECTURAS_POZO':
        prefijo='LEP'
    if tabla=='ESTIMACIONES_POZO':
        prefijo='ESP'
    if tabla=='PERDIDAS_POZO':
        prefijo='PEP'
    if tabla=='POTENCIAL_POZO':
        prefijo='POP'
    if tabla=='PRUEBAS_POZO':
        prefijo='PUP'
    return prefijo

#Salvar archivo
def save_file(name, content):
    """Decode and store a file uploaded with Plotly Dash."""
    data = content.encode("utf8").split(b";base64,")[0]
    with open(os.path.join(QUERY_DIRECTORY, name), "w") as fp:
       # fp.write(base64.decodebytes(data))
       fp.write(content)
    return

def search_list(list_search, list_input):
    flag = False
    # Using Counter
    
    if set(list_search).issubset(list_input):
        flag = True
    else:
        flag= False
    return flag

def update_columns_list(archivo, file_name, var_list):
    con = sqlite3.connect(archivo)

    query=''
    columns = [{'label': i, 'value': i} for i in []]
    #Listado de tablas en la BD
    cursor = con.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables_list = pd.DataFrame (cursor.fetchall(), columns = ['name'])
    tables_list = tables_list.sort_values('name')['name'].unique()

    if file_name:
        with open(os.path.join(QUERY_DIRECTORY, file_name)) as f:
            contenido = f.readlines()
            for linea in contenido:
                query +=  linea
            
            #Filtrar solo la primera fila
            query += " LIMIT 1"
            
            df =pd.read_sql(query, con)

        if var_list is not None:
            for columna in df.columns:
                if columna != 'FECHA' and columna != 'NOMBRE':
                    df[columna] = pd.to_numeric(df[columna])

            for var in var_list:
                requisitos_list, titulo, ecuacion = search_calcv( archivo, var)

                if search_list(requisitos_list, df.columns.tolist()):
                    evalu = eval(ecuacion)
                    df[titulo] = evalu

                if search_list(requisitos_list, tables_list):
                    #Buscar query en la tabla de Variables calculadas
                    #Modificar funcion para bsucar datos de variables calculadas
                    df[titulo]=""

        if  df.columns[2]=='FECHA':
            columns=[{'label': i, 'value': i} for i in df.columns[3:]]
        else:
            columns=[{'label': i, 'value': i} for i in df.columns[2:]]
            

    con.close()
    return columns

def find_file(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)

def read_select(table, fields, conditions):
    """ Generates SQL for a SELECT statement matching the kwargs passed. """
    sql = list()
    if fields:
      sql.append("SELECT " + ", ".join("%s" % (X) for X in fields))
      sql.append(" FROM %s " % table)
    else:
      sql.append("SELECT * FROM %s " % table)

    if conditions:
        sql.append("WHERE " + " AND ".join("%s" % (v) for v in conditions))

    return "".join(sql)


def create_list(item=None, value=None, operator=None):
  temp_list = list()
  if item is not None and value is not None and operator is not None:
    temp_list.append(item+operator+str(value))

def format_coefs(coefs):
    equation_list = [f"{coef}x^{i}" for i, coef in enumerate(coefs)]
    equation = "$" +  " + ".join(equation_list) + "$"

    replace_map = {"x^0": "", "x^1": "x", '+ -': '- '}
    for old, new in replace_map.items():
        equation = equation.replace(old, new)

    return equation