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
        basededatos = configuracion['BasedeDatos']['Destino']
        ruta = configuracion['BasedeDatos']['ruta']

    if 'fiscal' in configuracion:
        read_fiscal = configuracion['fiscal']['read']
        update_fiscal = configuracion['fiscal']['insert']

    if 'estimaciones' in configuracion:
        read_estimaciones = configuracion['estimaciones']['read']
        update_estimaciones = configuracion['estimaciones']['insert']

    if 'lecturas' in configuracion:
        read_lecturas = configuracion['lecturas']['read']
        update_lecturas = configuracion['lecturas']['insert']

    if 'potencial' in configuracion:
        read_potencial = configuracion['potencial']['read']
        update_potencial = configuracion['potencial']['insert']

    if 'pruebas' in configuracion:
        read_pruebas = configuracion['pruebas']['read']
        update_pruebas = configuracion['pruebas']['insert']

    if 'perdidas' in configuracion:
        read_perdidas = configuracion['perdidas']['read']
        update_perdidas = configuracion['perdidas']['insert']

#Crea la BD de SQLite en la ruta establecida en el archivo de configuracion

archivo = ruta +  basededatos        

#Conexion a la BD local
con = sqlite3.connect(archivo)

#Extrae la maxima fecha de la BD para actualizar los a partir de dicha fecha
cursor = con.execute("SELECT MAX(FECHA) FROM CIERRE_DIARIO_POZO")
dstart = cursor.fetchall()
#dstart = '2021-09-30 00:00:00'

#conectando al servidor SQL Server y leyendo datos
try:

    SQLPd=pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+Origen+';DATABASE='+Catalogo+';UID=pdmsadm;PWD='+ Password)
    print("Conexion exitosa a la BD: "+ Origen)

    #Leyendo los datos de Iems
    #df_items=pd.read_sql_query(read_items.format(dstart),SQLPd)

    #Leyendo los datos de produccion fiscal
    df_fiscal=pd.read_sql_query(read_fiscal.format(dstart),SQLPd)

    #Leyendo los datos de estimaciones de produccion
    df_estimaciones=pd.read_sql_query(read_estimaciones.format(dstart),SQLPd)

    #Leyendo los datos de lecturas
    df_lecturas=pd.read_sql_query(read_lecturas.format(dstart),SQLPd)

    #Leyendo los datos de potencial
    df_potencial=pd.read_sql_query(read_potencial.format(dstart),SQLPd)

    #Leyendo los datos de pruebas
    df_pruebas=pd.read_sql_query(read_pruebas.format(dstart),SQLPd)

    #Leyendo los datos de perdidas
    df_perdidas=pd.read_sql_query(read_perdidas.format(dstart),SQLPd)

except Exception as e:
    print('ERROR: %s',e)

print(df_fiscal)

#Crea las tablas en SQLite partiendo de los dataframe previamente cargados

sqlite_table = "ITEMS"
#df_items.to_sql(sqlite_table, con, if_exists='append')

sqlite_table = "CIERRE_DIARIO_POZO"
df_fiscal.to_sql(sqlite_table, con, if_exists='append')

sqlite_table = "ESTIMACIONES_POZO"
df_estimaciones.to_sql(sqlite_table, con, if_exists='append')

sqlite_table = "LECTURAS_POZO"
df_lecturas.to_sql(sqlite_table, con, if_exists='append')

sqlite_table = "POTENCIAL_POZO"
df_potencial.to_sql(sqlite_table, con, if_exists='append')

sqlite_table = "PRUEBAS_POZO"
df_pruebas.to_sql(sqlite_table, con, if_exists='append')

sqlite_table = "PERDIDAS_POZO"
df_perdidas.to_sql(sqlite_table, con, if_exists='append')

con.commit()
# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
con.close()
