import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Row import Row
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import base64
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import configparser
import sys
import os.path
import os
import pandas as pd
from datetime import date

from app import app 

#Define el nombre de las imagenes que mostraran en el dashboard
gas_png = 'D:\Proyectos\Ejemplos\pictures\gas.png'
cond_png = 'D:\Proyectos\Multipage_App\pictures\condensado.png'
wat_png = 'D:\Proyectos\Multipage_App\pictures\water.png'
perd_png = 'D:\Proyectos\Multipage_App\pictures\perdidas.png'
pot_png = 'D:\Proyectos\Multipage_App\pictures\potencial.png'
press_png = 'D:\Proyectos\Multipage_App\pictures\pressure.png'
temp_png = 'D:\Proyectos\Multipage_App\pictures\ptermometro.png'
choke_png = 'D:\Proyectos\Multipage_App\pictures\choke.png'

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


cards2 = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(dbc.Card([
                        dbc.CardHeader(html.Label(['Presion Cabezal'],style={'font-weight': 'bold', "text-align": "left"})),
                        dbc.CardBody(
                            [
                            dbc.Row([
                                    dbc.Col(
                                        dbc.CardImg(src='data:image/png;base64,{}'.format(press_base64), top=True, style={"width":"10rem"}),
                                    ),
                                    dbc.Col(
                                        html.Label(id='ind-whp',style={'font-weight': 'bold', "text-align": "left", "color":"blue"},
                                         children='Seleccione un pozo para actualizar')
                                    )
                                ], justify="center",)
                            ]
                        ),
                ], color="light", )),
                dbc.Col(dbc.Card([
                        dbc.CardHeader(html.Label(['Presion Linea'],style={'font-weight': 'bold', "text-align": "left"})),
                        dbc.CardBody(
                            [
                            dbc.Row([
                                    dbc.Col(
                                        dbc.CardImg(src='data:image/png;base64,{}'.format(press_base64), top=True, style={"width":"10rem"}),
                                    ),
                                    dbc.Col(
                                        html.Label(id='ind-pline',style={'font-weight': 'bold', "text-align": "left", "color":"blue"},
                                         children='Seleccione un pozo para actualizar')
                                    )
                                ], justify="center",)
                            ]
                        ),
                ], color="light")),
                dbc.Col(dbc.Card([
                        dbc.CardHeader(html.Label(['Presion Tubing'],style={'font-weight': 'bold', "text-align": "left"})),
                        dbc.CardBody(
                            [
                            dbc.Row([
                                    dbc.Col(
                                        dbc.CardImg(src='data:image/png;base64,{}'.format(press_base64), top=True, style={"width":"10rem"}),
                                    ),
                                    dbc.Col(
                                        html.Label(id='ind-ptub',style={'font-weight': 'bold', "text-align": "left", "color":"blue"},
                                         children='Seleccione un pozo para actualizar')
                                    )
                                ], justify="center",)
                            ]
                        ),
                ], color="light")),
            ],
            className="mb-4",
        ),
        dbc.Row(
            [
                dbc.Col(dbc.Card([
                        dbc.CardHeader(html.Label(['Presion Casing A'],style={'font-weight': 'bold', "text-align": "left"})),
                        dbc.CardBody(
                            [
                            dbc.Row([
                                    dbc.Col(
                                        dbc.CardImg(src='data:image/png;base64,{}'.format(press_base64), top=True, style={"width":"10rem"}),
                                    ),
                                    dbc.Col(
                                        html.Label(id='ind-pcasa',style={'font-weight': 'bold', "text-align": "left", "color":"blue"},
                                         children='Seleccione un pozo para actualizar')
                                    )
                                ], justify="center",)
                            ]
                        ),
                ], color="light")),
                dbc.Col(dbc.Card([
                        dbc.CardHeader(html.Label(['Presion Casing B'],style={'font-weight': 'bold', "text-align": "left"})),
                        dbc.CardBody(
                            [
                            dbc.Row([
                                    dbc.Col(
                                        dbc.CardImg(src='data:image/png;base64,{}'.format(press_base64), top=True, style={"width":"10rem"}),
                                    ),
                                    dbc.Col(
                                        html.Label(id='ind-pcasb',style={'font-weight': 'bold', "text-align": "left", "color":"blue"},
                                         children='Seleccione un pozo para actualizar')
                                    )
                                ], justify="center",)
                            ]
                        ),
                ], color="light")),
                dbc.Col(dbc.Card([
                        dbc.CardHeader(html.Label(['Presion Casing C'],style={'font-weight': 'bold', "text-align": "left"})),
                        dbc.CardBody(
                            [
                            dbc.Row([
                                    dbc.Col(
                                        dbc.CardImg(src='data:image/png;base64,{}'.format(press_base64), top=True, style={"width":"10rem"}),
                                    ),
                                    dbc.Col(
                                        html.Label(id='ind-pcasc',style={'font-weight': 'bold', "text-align": "left", "color":"blue"},
                                         children='Seleccione un pozo para actualizar')
                                    )
                                ], justify="center",)
                            ]
                        ),
                ], color="light")),
            ],
            className="mb-4",
        ),
        dbc.Row(
            [
                dbc.Col(dbc.Card([
                        dbc.CardHeader(html.Label(['Temp. Fondo A'],style={'font-weight': 'bold', "text-align": "left"})),
                        dbc.CardBody(
                            [
                            dbc.Row([
                                    dbc.Col(
                                        dbc.CardImg(src='data:image/png;base64,{}'.format(temp_base64), top=True, style={"width":"3rem"}),
                                    ),
                                    dbc.Col(
                                        html.Label(id='ind-tempa',style={'font-weight': 'bold', "text-align": "left", "color":"blue"},
                                         children='Seleccione un pozo para actualizar')
                                    )
                                ], justify="center",)
                            ]
                        ),
                ], color="light")),
                dbc.Col(dbc.Card([
                        dbc.CardHeader(html.Label(['Temp. Fondo B'],style={'font-weight': 'bold', "text-align": "left"})),
                        dbc.CardBody(
                            [
                            dbc.Row([
                                    dbc.Col(
                                        dbc.CardImg(src='data:image/png;base64,{}'.format(temp_base64), top=True, style={"width":"3rem", 'textAlign': 'center'}),
                                    ),
                                    dbc.Col(
                                        html.Label(id='ind-tempb',style={'font-weight': 'bold', "text-align": "left", "color":"blue"},
                                         children='Seleccione un pozo para actualizar')
                                    )
                                ], justify="center",)
                            ]
                        ),
                ], color="light")),
                dbc.Col(dbc.Card([
                        dbc.CardHeader(html.Label(['Choke'],style={'font-weight': 'bold', "text-align": "left"})),
                        dbc.CardBody(
                            [
                            dbc.Row([
                                    dbc.Col(
                                        dbc.CardImg(src='data:image/png;base64,{}'.format(choke_base64), top=True, style={"width":"6rem"}),
                                    ),
                                    dbc.Col(
                                        html.Label(id='ind-choke',style={'font-weight': 'bold', "text-align": "left", "color":"blue","font-size": "14px"},
                                         children='Seleccione un pozo para actualizar')
                                    )
                                ], justify="center",)
                            ]
                        ),
                ], color="light")),
            ]
        ),
    ]
)

#**** Cabecera de la pagina
cabecera = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(dbc.Card([
                    
                    dbc.CardHeader([dbc.CardImg(src='data:image/png;base64,{}'.format(gas_base64), top=True, style={"width":"1.5rem"})," Gas Producido"]),
                    dbc.CardBody(
                        [
                            html.H6(id='ind-prodgas',style={'font-weight': 'bold', "text-align": "left", "color":"white"},
                                         children='Seleccione un pozo para actualizar')
                        ]
                    ),
                ], )
                ),
                dbc.Col(dbc.Card([  
                    dbc.CardHeader([dbc.CardImg(src='data:image/png;base64,{}'.format(cond_base64), top=True, style={"width":"1.5rem"})," Condensado Producido"]),
                    dbc.CardBody(
                        [
                            html.H6(id='ind-prodcond',style={'font-weight': 'bold', "text-align": "left", "color":"white"},
                                         children='Seleccione un pozo para actualizar')
                        ]
                    ),
                ], )),
                dbc.Col(dbc.Card([  
                    dbc.CardHeader([dbc.CardImg(src='data:image/png;base64,{}'.format(wat_base64), top=True, style={"width":"1.5rem"})," Agua Producido"]),
                    dbc.CardBody(
                        [
                            html.H6(id='ind-prodwat',style={'font-weight': 'bold', "text-align": "left", "color":"white"},
                                         children='Seleccione un pozo para actualizar')
                        ]
                    ),
                ], )),
                dbc.Col(dbc.Card([  
                    dbc.CardHeader([dbc.CardImg(src='data:image/png;base64,{}'.format(perd_base64), top=True, style={"width":"2rem"})," Perdidas"]),
                    dbc.CardBody(
                        [
                            html.H6(id='ind-perdidas',style={'font-weight': 'bold', "text-align": "left", "color":"white"},
                                         children='Seleccione un pozo para actualizar')
                        ]
                    ),
                ], )),
                dbc.Col(dbc.Card([  
                    dbc.CardHeader([dbc.CardImg(src='data:image/png;base64,{}'.format(pot_base64), top=True, style={"width":"2rem"})," Potencial"]),
                    dbc.CardBody(
                        [
                            html.H6(id='ind-potencial',style={'font-weight': 'bold', "text-align": "left", "color":"white"},
                                         children='Seleccione un pozo para actualizar')
                        ]
                    ),
                ], )),
            ],
            className="mb-4",
        ),
    ]
)

layout = html.Div(
    [
        dbc.Row([
            html.Div(
                dbc.Col([
                    html.Label(['Pozos: '],style={'font-weight': 'bold', "text-align": "left"}),
                    dcc.Dropdown(
                        id='pozos-dropdown',
                        clearable=False,
                        options=[
                            {'label': 'Perla-1X', 'value': 'Perla-1X'},
                            {'label': 'Perla-5', 'value': 'Perla-5'},
                            {'label': 'Perla-6', 'value': 'Perla-6'},
                            {'label': 'Perla-7', 'value': 'Perla-7'},
                            {'label': 'Perla-9', 'value': 'Perla-9'},
                            {'label': 'Perla-10', 'value': 'Perla-10'}
                        ],
                        value="Perla-1X",
                        style={'height': '35px', 'width':'110px', 'font-size': '8'}
                    ),
                ]),
            ),
            html.Div([
                html.Label(['Fecha: '],style={'font-weight': 'bold', "text-align": "left"}),
                dcc.DatePickerSingle(
                    date=date.today(),
                    display_format='YYYY-MM-DD',
                    style={'backgroundColor':'white'},
                )
            ])
        ]),
        html.Br(),
        cabecera,
        html.Br(),
        dbc.Row([
            dbc.Col(
                cards2
            ),
            dbc.Col([
                dbc.Row(
                    dbc.Card([
            
                        dbc.CardBody(
                            [
                                dcc.Graph(id='prod-chart'),
                            ]
                        ), 
                    ], style={"width": "65rem"},),
                ),
                dbc.Row(
                    dbc.Card([
            
                        dbc.CardBody(
                            [
                                dcc.Graph(id='nodal-chart'),
                            ]
                        )
                    ]),
                ),
            ])
        ], className="mb-4"),
        dcc.Interval(id='update', n_intervals=0, interval=1000*5)
    ],
)

@app.callback(
    Output('prod-chart','figure'),
    [Input('pozos-dropdown', 'value')]
    )
def update_line_chart(pozo):

    #Extrae la maxima fecha de la BD para actualizar los a partir de dicha fecha
    #Conexion a la BD local
    if pozo:
        con = sqlite3.connect(archivo)
        cursor = con.execute("SELECT FECHA, TASA_GAS FROM CIERRE_DIARIO_POZO WHERE NOMBRE='"+pozo+"' AND FECHA>= date(DATE('now'), '-30 day') GROUP BY FECHA")
        gas_producido = pd.DataFrame (cursor.fetchall(), columns = ['FECHA', 'TASA_GAS'])
        figura = px.line(gas_producido, x="FECHA", y="TASA_GAS",title="Gas Producido")
        figura.update_layout(
            font_family="Courier New",
            font_color="blue",
            title_font_family="Times New Roman",
            title_font_color="red",
            legend_title_font_color="green"
        )
    else:
        figura ={}
    return figura


@app.callback(
    [dash.dependencies.Output('ind-whp', 'children'),
    dash.dependencies.Output('ind-pline', 'children'),
    dash.dependencies.Output('ind-ptub', 'children'),
    dash.dependencies.Output('ind-pcasa', 'children'),
    dash.dependencies.Output('ind-pcasb', 'children'),
    dash.dependencies.Output('ind-pcasc', 'children'),
    dash.dependencies.Output('ind-tempa', 'children'),
    dash.dependencies.Output('ind-tempb', 'children'),
    dash.dependencies.Output('ind-choke', 'children'),
    dash.dependencies.Output('ind-prodgas', 'children'),
    dash.dependencies.Output('ind-prodcond', 'children'),
    dash.dependencies.Output('ind-prodwat', 'children'),
    dash.dependencies.Output('ind-perdidas', 'children'),
    dash.dependencies.Output('ind-potencial', 'children')],
    [Input('pozos-dropdown', 'value')]
)
def update_output(pozo):
    con = sqlite3.connect(archivo)

    cursor = con.execute("SELECT PRESION_CABEZAL FROM LECTURAS_POZO WHERE NOMBRE='"+pozo+"' AND FECHA>='2021-10-05 00:00:00'")
    valor= cursor.fetchall()
    if valor:
        for data in valor:
            valor_whp = ' {} psig'.format(data[0])
    else:
        valor_whp = ""

    cursor = con.execute("SELECT PRESION_LINEA FROM LECTURAS_POZO WHERE NOMBRE='"+pozo+"' AND FECHA>='2021-10-05 00:00:00'")
    valor= cursor.fetchall()
    if valor:
        for data in valor:
            valor_pline = ' {} psig'.format(round(data[0],2))
    else:
        valor_pline = ""

    cursor = con.execute("SELECT PRESION_TUBING FROM LECTURAS_POZO WHERE NOMBRE='"+pozo+"' AND FECHA>='2021-10-05 00:00:00'")
    valor= cursor.fetchall()
    if valor:
        for data in valor:
            valor_ptub = ' {} psig'.format(data[0])
    else:
        valor_ptub = ""

    cursor = con.execute("SELECT PRESION_CASING_A FROM LECTURAS_POZO WHERE NOMBRE='"+pozo+"' AND FECHA>='2021-10-05 00:00:00'")
    valor= cursor.fetchall()
    if valor:
        for data in valor:
            valor_pcasa = ' {} psig'.format(data[0])
    else:
        valor_pcasa = ""

    cursor = con.execute("SELECT PRESION_CASING_B FROM LECTURAS_POZO WHERE NOMBRE='"+pozo+"' AND FECHA>='2021-10-05 00:00:00'")
    valor= cursor.fetchall()
    if valor:
        for data in valor:
            valor_pcasb = ' {} psig'.format(data[0])
    else:
        valor_pcasb = ""

    cursor = con.execute("SELECT PRESION_CASING_C FROM LECTURAS_POZO WHERE NOMBRE='"+pozo+"' AND FECHA>='2021-10-05 00:00:00'")
    valor= cursor.fetchall()
    if valor:
        for data in valor:
            valor_pcasc = ' {} psig'.format(data[0])
    else:
        valor_pcasc = ""

    cursor = con.execute("SELECT TEMP_FONDO_A FROM LECTURAS_POZO WHERE NOMBRE='"+pozo+"' AND FECHA>='2021-10-05 00:00:00'")
    valor= cursor.fetchall()
    if valor:
        for data in valor:
            valor_tempa = '   {} °F'.format(data[0])
    else:
        valor_tempa = ""

    cursor = con.execute("SELECT TEMP_FONDO_B FROM LECTURAS_POZO WHERE NOMBRE='"+pozo+"' AND FECHA>='2021-10-05 00:00:00'")
    valor= cursor.fetchall()
    if valor:
        for data in valor:
            valor_tempb = '   {} °F'.format(data[0])
    else:
        valor_tempb = ""
    
    cursor = con.execute("SELECT CHOKE FROM LECTURAS_POZO WHERE NOMBRE='"+pozo+"' AND FECHA>='2021-10-05 00:00:00'")
    valor= cursor.fetchall()
    if valor:
        for data in valor:
            valor_choke = ' {} %'.format(round(data[0],2))
    else:
        valor_choke = ""
    
    cursor = con.execute("SELECT TASA_GAS FROM CIERRE_DIARIO_POZO WHERE NOMBRE='"+pozo+"' AND FECHA='2021-10-04 00:00:00'")
    valor= cursor.fetchall()
    if valor:
        for data in valor:
            valor_prodgas = ' {} MMPCD'.format(data[0])
    else:
        valor_prodgas = ""
    
    cursor = con.execute("SELECT TASA_CONDENSADO FROM CIERRE_DIARIO_POZO WHERE NOMBRE='"+pozo+"' AND FECHA='2021-10-04 00:00:00'")
    valor= cursor.fetchall()
    if valor:
        for data in valor:
            valor_prodcond = ' {} BLS'.format(data[0])
    else:
        valor_prodcond = ""
    
    cursor = con.execute("SELECT TASA_AGUA FROM CIERRE_DIARIO_POZO WHERE NOMBRE='"+pozo+"' AND FECHA='2021-10-04 00:00:00'")
    valor= cursor.fetchall()
    for data in valor:
        valor_prodwat = ' {} BLS'.format(data[0])

    cursor = con.execute("SELECT TASA_AGUA FROM CIERRE_DIARIO_POZO WHERE NOMBRE='"+pozo+"' AND FECHA='2021-10-04 00:00:00'")
    valor= cursor.fetchall()
    if valor:
        for data in valor:
            valor_perdidas = ' {} MMPCD'.format(data[0])
    else:
        valor_perdidas = ""
    
    cursor = con.execute("SELECT VOLUMEN_GAS FROM POTENCIAL_POZO WHERE NOMBRE='"+pozo+"' ORDER BY FECHA DESC LIMIT 1")
    valor= cursor.fetchall()

    if valor:
        for data in valor:
            valor_potencial = ' {} MMPCD'.format(data[0])
    else:
        valor_potencial = ""

    return valor_whp, valor_pline, valor_ptub, valor_pcasa, valor_pcasb, valor_pcasc, valor_tempa, valor_tempb, valor_choke, valor_prodgas, valor_prodcond, valor_prodwat, valor_perdidas, valor_potencial

