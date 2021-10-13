import pyodbc 
import pandas as pd

conexion = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=SVPTG01PMS91\MSSQLSERVER_PMS' + 
';DATABASE=PDMS;UID=pdmsadm;PWD=Card0n2021$06')

atributos = pd.read_sql_query("SELECT COLUMN_NAME, TABLE_NAME FROM INFORMATION_SCHEMA.COLUMNS  WHERE  COLUMN_NAME NOT IN  ('ITEMID','NOMBRE', 'FLUIDO','FUNCION')",conexion)

vista='ESTIMACIONES_POZO'
columns_names=atributos[atributos['TABLE_NAME']==vista]['COLUMN_NAME']
columns_names_list = list(columns_names)
print(columns_names_list)