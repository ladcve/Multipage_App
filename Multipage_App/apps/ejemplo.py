import dash
from dash.dependencies import Input, Output
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import pyodbc 

conexion = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=SVPTG01PMS91\MSSQLSERVER_PMS' + 
';DATABASE=PDMS;UID=pdmsadm;PWD=Card0n2021$06')

df = pd.read_sql_query("SELECT * FROM CIERRE_DIARIO_POZO WHERE ITEMID IN (13,23,40) ORDER BY FECHA",conexion)

app = dash.Dash(__name__)

PAGE_SIZE = 5

app.layout = html.Div([
    dash_table.DataTable(
        id='datatable-paging-page-count',
        columns=[
            {"name": i, "id": i} for i in sorted(df.columns)
        ],
        page_current=0,
        page_size=PAGE_SIZE,
        page_action='custom'
    ),
    html.Br(),
    dcc.Checklist(
        id='datatable-use-page-count',
        options=[
            {'label': 'Use page_count', 'value': 'True'}
        ],
        value=['True']
    ),
    'Page count: ',
    dcc.Input(
        id='datatable-page-count',
        type='number',
        min=1,
        max=29,
        value=20
    )
])


@app.callback(
    Output('datatable-paging-page-count', 'data'),
    Input('datatable-paging-page-count', "page_current"),
    Input('datatable-paging-page-count', "page_size"))
def update_table(page_current,page_size):
    return df.iloc[
        page_current*page_size:(page_current+ 1)*page_size
    ].to_dict('records')

@app.callback(
    Output('datatable-paging-page-count', 'page_count'),
    Input('datatable-use-page-count', 'value'),
    Input('datatable-page-count', 'value'))
def update_table(use_page_count, page_count_value):
    if len(use_page_count) == 0 or page_count_value is None:
        return None
    return page_count_value

if __name__ == '__main__':
    app.run_server(debug=True)