import os
from textwrap import dedent
import dash_bootstrap_components as dbc
import dash_player
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State


from app import app

layout = html.Div(children = [
        dbc.Row([
                dbc.Col([
                    dcc.Markdown(dedent('''
                        ### Video de presentacion Production Analysis
                        ##### Que es Production Analysis?
                        '''))
                ]),
                dbc.Col([
                    dash_player.DashPlayer(
                        id='video-player',
                        url='https://youtu.be/SzvoyTz4IPg',
                        controls=True,
                        width='70%'
                    ),
                    html.Div(
                        id='div-current-time',
                        style={'margin': '10px 0px'}
                    ),
                ]),
        ]),
        dbc.Row([
                dbc.Col([
                    dcc.Markdown(dedent('''
                        ### Conceptos basicos 
                        ##### De donde vienen los datos?
                        ##### Como se extraen los datos para ser visualizados?
                        ##### Como se visualizan?
                        ##### Respondiendo a estas y otras interrogantes
                        '''))
                ]),
                dbc.Col([
                    dash_player.DashPlayer(
                        id='video-player',
                        url='https://youtu.be/KUR15AZ2MB4',
                        controls=True,
                        width='70%'
                    ),
                    html.Div(
                        id='div-current-time',
                        style={'margin': '10px 0px'}
                    ),
                ]),
        ]),
        dbc.Row([
                dbc.Col([
                    dcc.Markdown(dedent('''
                        ### Dashboard 
                        ##### el dashboard es una manera rápida y eficiente
                        ##### de ver los datos en una sola pantalla,
                        ##### puede visualizar múltiples gráficos
                        
                        '''))
                ]),
                dbc.Col([
                    dash_player.DashPlayer(
                        id='video-player',
                        url='https://youtu.be/PSEdnE24yVw',
                        controls=True,
                        width='70%'
                    ),
                    html.Div(
                        id='div-current-time',
                        style={'margin': '10px 0px'}
                    ),
                ]),
        ]),
        dbc.Row([
                dbc.Col([
                    dcc.Markdown(dedent('''
                        ### Generación de Gráficos 
                        ##### En este video le explicamos como realizar gráficos,
                        ##### entender el proceso es sencillo y puede ser aplicado
                        ##### para todos los tipos de graficos disponibles
                        '''))
                ]),
                dbc.Col([
                    dash_player.DashPlayer(
                        id='video-player',
                        url='https://youtu.be/MHcHOTN8dis',
                        controls=True,
                        width='70%'
                    ),
                    html.Div(
                        id='div-current-time',
                        style={'margin': '10px 0px'}
                    ),
                ]),
        ]),
        dbc.Row([
                dbc.Col([
                    dcc.Markdown(dedent('''
                        ### Generación de Reportes 
                        ##### Una manera de extraer datos, organizarlos y
                        ##### exportarlos es a tráves de reportes.
                        ##### Este video les muestra como poder generar rerpotes facilmente.
                        '''))
                ]),
                dbc.Col([
                    dash_player.DashPlayer(
                        id='video-player',
                        url='https://youtu.be/72rMhjKkKYw',
                        controls=True,
                        width='70%'
                    ),
                    html.Div(
                        id='div-current-time',
                        style={'margin': '10px 0px'}
                    ),
                ]),
        ]),
        dbc.Row([
                dbc.Col([
                    dcc.Markdown(dedent('''
                        ### Carga de datos manuales
                        ##### Incorporar los datos de subsuelo es vital para
                        ##### integrar todos los datos necesarios para un buen
                        ##### análisis. Este video explica como hacerlo.
                        '''))
                ]),
                dbc.Col([
                    dash_player.DashPlayer(
                        id='video-player',
                        url='https://youtu.be/27hQlFlT-AI', 
                        controls=True,
                        width='70%'
                    ),
                    html.Div(
                        id='div-current-time',
                        style={'margin': '10px 0px'}
                    ),
                ]),
        ]),
    ])

if __name__ == '__main__':
    app.run_server(debug=False)