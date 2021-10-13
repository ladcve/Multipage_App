# Objetivo: Rutina para crea basde de datos parcialmente similar a PDMS
# Fecha: Septiembre 2021
# Comentarios: 
# .- Se crearan las siguientes tablas provenientes de las vistas de PDMS
#    CIERRE_DIARIO_POZO
#    ESTIMACIONES_POZO
#    PRUEBAS_POZO
#    LECTURAS_DIARIAS_POZO
#    POTENCIAL_POZO
#    PERDIDAS_POZO
#    ITEMS (solo datos de pozos)

# referencias:
# https://www.fullstackpython.com/blog/export-pandas-dataframes-sqlite-sqlalchemy.html
# https://dash-bootstrap-components.opensource.faculty.ai/docs/components/button/


import sqlite3
import configparser
import sys
import os.path
import os
import pandas as pd
import pyodbc 

configuracion = configparser.ConfigParser()

if os.path.isfile('config.ini'):

    configuracion.read('config.ini')

    if 'BasedeDatos' in configuracion:
        Origen = configuracion['BasedeDatos']['Origen']
        Catalogo = configuracion['BasedeDatos']['Catalogo']
        Password = configuracion['BasedeDatos']['Password']
        ruta = configuracion['BasedeDatos']['ruta']

    if 'items' in configuracion:
        items = configuracion['items']['consulta']

    if 'fiscal' in configuracion:
        fiscal = configuracion['fiscal']['consulta']

    if 'estimaciones' in configuracion:
        estimaciones = configuracion['estimaciones']['consulta']

    if 'lecturas' in configuracion:
        lecturas = configuracion['lecturas']['consulta']

    if 'potencial' in configuracion:
        potencial = configuracion['potencial']['consulta']

    if 'pruebas' in configuracion:
        pruebas = configuracion['pruebas']['consulta']

    if 'perdidas' in configuracion:
        perdidas = configuracion['perdidas']['consulta']

#Crea la BD de SQLite en la ruta establecida en el archivo de configuracion
basededatos = '\ProdAnalysis.db'
archivo = ruta +  basededatos        

con = sqlite3.connect(archivo)

#conectando al servidor SQL Server y leyendo datos
try:

    SQLPd=pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+Origen+';DATABASE='+Catalogo+';UID=pdmsadm;PWD='+ Password)
    print("Conexion exitosa a la BD: "+ Origen)

    #Leyendo los datos de Iems
    df_items=pd.read_sql_query(items,SQLPd)

    #Leyendo los datos de produccion fiscal
    df_fiscal=pd.read_sql_query(fiscal,SQLPd)

    #Leyendo los datos de estimaciones de produccion
    df_estimaciones=pd.read_sql_query(estimaciones,SQLPd)

    #Leyendo los datos de lecturas
    df_lecturas=pd.read_sql_query(lecturas,SQLPd)

    #Leyendo los datos de potencial
    df_potencial=pd.read_sql_query(potencial,SQLPd)

    #Leyendo los datos de pruebas
    df_pruebas=pd.read_sql_query(pruebas,SQLPd)

    #Leyendo los datos de perdidas
    df_perdidas=pd.read_sql_query(perdidas,SQLPd)

except Exception as e:
    print('ERROR: %s',e)



#Crea las tablas en SQLite partiendo de los dataframe previamente cargados

sqlite_table = "ITEMS"
df_items.to_sql(sqlite_table, con, if_exists='replace')

sqlite_table = "CIERRE_DIARIO_POZO"
df_fiscal.to_sql(sqlite_table, con, if_exists='replace')

sqlite_table = "ESTIMACIONES_POZO"
df_estimaciones.to_sql(sqlite_table, con, if_exists='replace')

sqlite_table = "LECTURAS_POZO"
df_lecturas.to_sql(sqlite_table, con, if_exists='replace')

sqlite_table = "POTENCIAL_POZO"
df_potencial.to_sql(sqlite_table, con, if_exists='replace')

sqlite_table = "PRUEBAS_POZO"
df_pruebas.to_sql(sqlite_table, con, if_exists='replace')

sqlite_table = "PERDIDAS_POZO"
df_perdidas.to_sql(sqlite_table, con, if_exists='replace')

# tabla de trayectorias o surveys

con.execute('''CREATE TABLE IF NOT EXISTS SURVEY
               (NOMBRE text, MD decimal, INC DECIMAL, AZ DECIMAL, TVD DECIMAL, LOCAL_N DECIMAL, LOCAL_E DECIMAL,
               VSEC DECIMAL, DOGLEG DECIMAL)''')


# tabla de analisis nodal
con.execute('''CREATE TABLE IF NOT EXISTS NODAL
               (NOMBRE text, TASA_GAS decimal, VLP DECIMAL, IPR DECIMAL)''')

con.commit()
# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
con.close()
