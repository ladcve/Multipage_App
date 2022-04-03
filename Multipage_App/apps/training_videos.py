import os
from textwrap import dedent
import dash_bootstrap_components as dbc
import dash_player
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_admin_components as dac
from dash.dependencies import Input, Output, State


from app import app

layout = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dac.Box([
                    dac.BoxHeader(
                        collapsible = True,
                        closable = False,
                        title="Introduccion"
                    ),
                    dac.BoxBody([
                        dbc.Row([
                            dbc.Col([
                                dac.Box([
                                        dac.BoxHeader(
                                            collapsible = False,
                                            closable = False,
                                            title="Presentacion"
                                        ),
                                        dac.BoxBody([
                                            dash_player.DashPlayer(
                                                id='video-player',
                                                url='https://youtu.be/SzvoyTz4IPg',
                                                controls=True,
                                                width='100%'
                                            ),
                                            html.Div(
                                                id='div-current-time',
                                                style={'margin': '10px 0px'}
                                            ),
                                            dcc.Markdown(dedent('''
                                                ##### Video de presentacion Production Analysis
                                                ##### Que es Production Analysis?
                                            '''))
                                        ]),	
                                    ],
                                    color='primary',
                                    solid_header=True,
                                    elevation=4,
                                    width=12
                                ),
                            ]),
                            dbc.Col([
                                dac.Box([
                                        dac.BoxHeader(
                                            collapsible = False,
                                            closable = False,
                                            title="Conceptos basicos"
                                        ),
                                        dac.BoxBody([
                                            dash_player.DashPlayer(
                                                id='video-player',
                                                url='https://youtu.be/KUR15AZ2MB4',
                                                controls=True,
                                                width='100%'
                                            ),
                                            html.Div(
                                                id='div-current-time',
                                                style={'margin': '10px 0px'}
                                            ),
                                            dcc.Markdown(dedent('''
                                                ##### Conceptos basicos 
                                                ##### De donde vienen los datos?. Como se extraen los datos para ser visualizados? Como se visualizan?
                                                ##### Respondiendo a estas y otras interrogantes
                                                '''))
                                        ]),	
                                    ],
                                    color='primary',
                                    solid_header=True,
                                    elevation=4,
                                    width=12
                                ),
                            ]),
                        ]),
                    ]),
                ],
                color='primary',
                solid_header=True,
                elevation=4,
                width=12
                ),
            ]),
            dbc.Row([
                dbc.Col([
                    dac.Box([
                        dac.BoxHeader(
                            collapsible = True,
                            closable = False,
                            title="Visualización"
                        ),
                        dac.BoxBody([
                            dbc.Row([
                                dbc.Col([
                                    dac.Box([
                                            dac.BoxHeader(
                                                collapsible = False,
                                                closable = False,
                                                title="Dashboard"
                                            ),
                                            dac.BoxBody([
                                                dash_player.DashPlayer(
                                                    id='video-player',
                                                    url='https://youtu.be/PSEdnE24yVw',
                                                    controls=True,
                                                    width='100%'
                                                ),
                                                html.Div(
                                                    id='div-current-time',
                                                    style={'margin': '10px 0px'}
                                                ),
                                                dcc.Markdown(dedent('''
                                                    ##### Dashboard 
                                                    ##### el dashboard es una manera rápida y eficiente
                                                    ##### de ver los datos en una sola pantalla,
                                                    ##### puede visualizar múltiples gráficos
                                                '''))
                                            ]),	
                                        ],
                                        color='primary',
                                        solid_header=True,
                                        elevation=4,
                                        width=12
                                    ),
                                ]),
                                dbc.Col([
                                    dac.Box([
                                            dac.BoxHeader(
                                                collapsible = False,
                                                closable = False,
                                                title="Gráficos"
                                            ),
                                            dac.BoxBody([
                                                dash_player.DashPlayer(
                                                    id='video-player',
                                                    url='https://youtu.be/MHcHOTN8dis',
                                                    controls=True,
                                                    width='100%'
                                                ),
                                                html.Div(
                                                    id='div-current-time',
                                                    style={'margin': '10px 0px'}
                                                ),
                                                dcc.Markdown(dedent('''
                                                    ##### Generación de Gráficos 
                                                    ##### En este video le explicamos como realizar gráficos,
                                                    ##### entender el proceso es sencillo y puede ser aplicado
                                                    ##### para todos los tipos de graficos disponibles
                                                '''))
                                            ]),	
                                        ],
                                        color='primary',
                                        solid_header=True,
                                        elevation=4,
                                        width=12
                                    ),
                                ]),
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dac.Box([
                                            dac.BoxHeader(
                                                collapsible = False,
                                                closable = False,
                                                title="Reportes"
                                            ),
                                            dac.BoxBody([
                                                dash_player.DashPlayer(
                                                    id='video-player',
                                                    url='https://youtu.be/72rMhjKkKYw',
                                                    controls=True,
                                                    width='100%'
                                                ),
                                                html.Div(
                                                    id='div-current-time',
                                                    style={'margin': '10px 0px'}
                                                ),
                                                dcc.Markdown(dedent('''
                                                    ##### Generación de Reportes 
                                                    ##### Una manera de extraer datos, organizarlos y
                                                    ##### exportarlos es a tráves de reportes.
                                                    ##### Este video les muestra como poder generar rerpotes facilmente.
                                                '''))
                                            ]),	
                                        ],
                                        color='primary',
                                        solid_header=True,
                                        elevation=4,
                                        width=12
                                    ),
                                ]),
                                dbc.Col([
                                    dac.Box([
                                            dac.BoxHeader(
                                                collapsible = False,
                                                closable = False,
                                                title="Mapas"
                                            ),
                                            dac.BoxBody([
                                                dash_player.DashPlayer(
                                                    id='video-player',
                                                    url='https://youtu.be/AaZKl8GrHK8',
                                                    controls=True,
                                                    width='100%'
                                                ),
                                                html.Div(
                                                    id='div-current-time',
                                                    style={'margin': '10px 0px'}
                                                ),
                                                dcc.Markdown(dedent('''
                                                    ##### Generación de Mapas
                                                    ##### Generar mapas de contorno o superficie
                                                    ##### para visualizar datos en una forma representativa y
                                                    ##### versatil.
                                                '''))
                                            ]),	
                                        ],
                                        color='primary',
                                        solid_header=True,
                                        elevation=4,
                                        width=12
                                    ),
                                ]),
                            ]),
                        ]),
                    ],
                    color='primary',
                    solid_header=True,
                    elevation=4,
                    width=12
                    ),
                ]),
            ]),
            dbc.Row([
                dbc.Col([
                    dac.Box([
                        dac.BoxHeader(
                            collapsible = True,
                            closable = False,
                            title="Administración"
                        ),
                        dac.BoxBody([
                            dbc.Row([
                                dbc.Col([
                                    dac.Box([
                                            dac.BoxHeader(
                                                collapsible = False,
                                                closable = False,
                                                title="Variables Calculadas"
                                            ),
                                            dac.BoxBody([
                                                dash_player.DashPlayer(
                                                    id='video-player',
                                                    url='https://youtu.be/CJk1LlmK8qk',
                                                    controls=True,
                                                    width='100%'
                                                ),
                                                html.Div(
                                                    id='div-current-time',
                                                    style={'margin': '10px 0px'}
                                                ),
                                                dcc.Markdown(dedent('''
                                                    ##### Variables Calculadas 
                                                    ##### Son una manera de extender las capacidades
                                                    ##### de cálculo de la aplicación.
                                                '''))
                                            ]),	
                                        ],
                                        color='primary',
                                        solid_header=True,
                                        elevation=4,
                                        width=12
                                    ),
                                ]),
                                dbc.Col([
                                    dac.Box([
                                            dac.BoxHeader(
                                                collapsible = False,
                                                closable = False,
                                                title="SQL Builder"
                                            ),
                                            dac.BoxBody([
                                                dash_player.DashPlayer(
                                                    id='video-player',
                                                    url='https://youtu.be/lsD1RJ99-ro',
                                                    controls=True,
                                                    width='100%'
                                                ),
                                                html.Div(
                                                    id='div-current-time',
                                                    style={'margin': '10px 0px'}
                                                ),
                                                dcc.Markdown(dedent('''
                                                    ##### Generación de Consultas
                                                    ##### Una de las potencialidades de Production Analysis
                                                    ##### es poder contruir consultas para extraer los datos
                                                    ##### almacenados
                                                '''))
                                            ]),	
                                        ],
                                        color='primary',
                                        solid_header=True,
                                        elevation=4,
                                        width=12
                                    ),
                                ]),
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dac.Box([
                                            dac.BoxHeader(
                                                collapsible = False,
                                                closable = False,
                                                title="Actualizar DB"
                                            ),
                                            dac.BoxBody([
                                                dash_player.DashPlayer(
                                                    id='video-player',
                                                    url='https://youtu.be/72rMhjKkKYw',
                                                    controls=True,
                                                    width='100%'
                                                ),
                                                html.Div(
                                                    id='div-current-time',
                                                    style={'margin': '10px 0px'}
                                                ),
                                                dcc.Markdown(dedent('''
                                                    ##### Generación de Reportes 
                                                    ##### Una manera de extraer datos, organizarlos y
                                                    ##### exportarlos es a tráves de reportes.
                                                    ##### Este video les muestra como poder generar rerpotes facilmente.
                                                '''))
                                            ]),	
                                        ],
                                        color='primary',
                                        solid_header=True,
                                        elevation=4,
                                        width=12
                                    ),
                                ]),
                                dbc.Col([
                                    dac.Box([
                                            dac.BoxHeader(
                                                collapsible = False,
                                                closable = False,
                                                title="Exportar Datos"
                                            ),
                                            dac.BoxBody([
                                                dash_player.DashPlayer(
                                                    id='video-player',
                                                    url='https://youtu.be/b2T4WMNu5i8',
                                                    controls=True,
                                                    width='100%'
                                                ),
                                                html.Div(
                                                    id='div-current-time',
                                                    style={'margin': '10px 0px'}
                                                ),
                                                dcc.Markdown(dedent('''
                                                    ##### Generación de Mapas
                                                    ##### Generar mapas de contorno o superficie
                                                    ##### para visualizar datos en una forma representativa y
                                                    ##### versatil.
                                                '''))
                                            ]),	
                                        ],
                                        color='primary',
                                        solid_header=True,
                                        elevation=4,
                                        width=12
                                    ),
                                ]),
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dac.Box([
                                            dac.BoxHeader(
                                                collapsible = False,
                                                closable = False,
                                                title="Unidades"
                                            ),
                                            dac.BoxBody([
                                                dash_player.DashPlayer(
                                                    id='video-player',
                                                    url='https://youtu.be/72rMhjKkKYw',
                                                    controls=True,
                                                    width='100%'
                                                ),
                                                html.Div(
                                                    id='div-current-time',
                                                    style={'margin': '10px 0px'}
                                                ),
                                                dcc.Markdown(dedent('''
                                                    ##### Generación de Reportes 
                                                    ##### Una manera de extraer datos, organizarlos y
                                                    ##### exportarlos es a tráves de reportes.
                                                    ##### Este video les muestra como poder generar rerpotes facilmente.
                                                '''))
                                            ]),	
                                        ],
                                        color='primary',
                                        solid_header=True,
                                        elevation=4,
                                        width=12
                                    ),
                                ]),
                                dbc.Col([
                                    dac.Box([
                                            dac.BoxHeader(
                                                collapsible = False,
                                                closable = False,
                                                title="Vacio"
                                            ),
                                            dac.BoxBody([
                                                dash_player.DashPlayer(
                                                    id='video-player',
                                                    url='https://youtu.be/AaZKl8GrHK8',
                                                    controls=True,
                                                    width='100%'
                                                ),
                                                html.Div(
                                                    id='div-current-time',
                                                    style={'margin': '10px 0px'}
                                                ),
                                                dcc.Markdown(dedent('''
                                                    ##### Generación de Mapas
                                                    ##### Generar mapas de contorno o superficie
                                                    ##### para visualizar datos en una forma representativa y
                                                    ##### versatil.
                                                '''))
                                            ]),	
                                        ],
                                        color='primary',
                                        solid_header=True,
                                        elevation=4,
                                        width=12
                                    ),
                                ]),
                            ]),
                        ]),
                    ],
                    color='primary',
                    solid_header=True,
                    elevation=4,
                    width=12
                    ),
                ]),
            ]),
        ], width={"size": 6, "offset": 0}),
        
        dbc.Col([
            dac.Box([
                dac.BoxHeader(
                    collapsible = True,
                    closable = False,
                    title="Ingeniería"
                ),
                dac.BoxBody([
                    dbc.Row([
                        dbc.Col([
                            dac.Box([
                                    dac.BoxHeader(
                                        collapsible = False,
                                        closable = False,
                                        title="Declinación"
                                    ),
                                    dac.BoxBody([
                                        dash_player.DashPlayer(
                                            id='video-player',
                                            url='https://youtu.be/GBeKjySZTw4', 
                                            controls=True,
                                            width='100%'
                                        ),
                                        html.Div(
                                            id='div-current-time',
                                            style={'margin': '10px 0px'}
                                        ),
                                        dcc.Markdown(dedent('''
                                        ##### Análisis de Declinación
                                        ##### Las curvas de declinación permiten estimar las reservas a recuperar 
                                        ##### durante la vida productiva y hacer comparaciones con los estimados 
                                        ##### por otros métodos como el balance de materiales.
                                        '''))
                                    ]),	
                                ],
                                color='primary',
                                solid_header=True,
                                elevation=4,
                                width=12
                            ),
                        ]),
                        dbc.Col([
                            dac.Box([
                                    dac.BoxHeader(
                                        collapsible = False,
                                        closable = False,
                                        title="Conceptos basicos"
                                    ),
                                    dac.BoxBody([
                                        dash_player.DashPlayer(
                                            id='video-player',
                                            url='https://youtu.be/KUR15AZ2MB4',
                                            controls=True,
                                            width='100%'
                                        ),
                                        html.Div(
                                            id='div-current-time',
                                            style={'margin': '10px 0px'}
                                        ),
                                    ]),	
                                ],
                                color='primary',
                                solid_header=True,
                                elevation=4,
                                width=12
                            ),
                        ]),
                    ]),
                ]),
            ],
            color='primary',
            solid_header=True,
            elevation=4,
            width=12
            ),
        ], width={"size": 6, "offset": 0}),
    ]),
    dbc.Modal(
        [
            dbc.ModalHeader("Consulta guardada"),
        ],
        id="modal_sql",
        is_open=False,
    ),
])

if __name__ == '__main__':
    app.run_server(debug=False)