"""
Modulo: Index
------------------------------
"""

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import sys
import base64
import datetime
import webbrowser



# Connect to main app.py file
from app import app

# Connect to your app pages
from apps import report_builder, multi_line_chart, line_chart, bar_chart, sunburst_chart, events_loader, survey_loader, dashboard, sql_builder2, decline_analysis, contour_map, scatter_chart, area_chart, wellbore_diagram, wellbore_loader, LAS_chart, cross_section, items_loader, db_creation_update, variable_loader, python_interprete, export_data, nodal, markers_loader, units_loader, mdt_loader

app.css.config.serve_locally = True
app.scripts.config.serve_locally = True


logo_filename = '.\pictures\LogoProdAnalysis.png'
home_filename = '.\pictures\home.png'
logo_base64 = base64.b64encode(open(logo_filename, 'rb').read()).decode('ascii')
home_base64 = base64.b64encode(open(home_filename, 'rb').read()).decode('ascii')

navbar = dbc.Navbar(
    [
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(html.Img(src='data:image/png;base64,{}'.format(logo_base64))),
                    dbc.Col(dbc.NavbarBrand(html.H5(['  Production Analysis'],style={'font-weight': 'bold', "text-align": "left"}), className="ml-2")),
                    dbc.Col(dbc.NavbarBrand(html.Div(id="screen_name"), className="ml-2", style={'font-weight': 'bold', "text-align": "left"})),
                ],
                align="center",
                #no_gutters=True,
            ),
        ),
    ],
    color="dark",
    dark=True,
)

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 59,
    "left": 0,
    "bottom": 0,
    "width": "18rem",
    "padding": "2rem 1rem",
    "background-color": "#D5DBDB",
    "font-weight": "bold",
    "overflow": "scroll",
    "font-size": "32px; ",
}

# padding for the page content
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "1rem 1rem",
}

submenu_graficos = [
    html.Li(
        "Gráficos",
        style={"cursor": "pointer"},
        id="submenu-1",
    ),
    # we use the Collapse component to hide and reveal the navigation links
    dbc.Collapse(
        [
            dbc.NavLink("Dashboard", href="/", active="exact"),
            dbc.NavLink("Línea", href="/apps/line_chart", active="exact"),
            dbc.NavLink("Multi Gráfico Línea", href="/apps/multi_line_chart", active="exact"),
            dbc.NavLink("Barras", href="/apps/bar_chart", active="exact"),
            dbc.NavLink("Scatter", href="/apps/scatter_chart", active="exact"),
            dbc.NavLink("Sunburst", href="/apps/sunburst_chart", active="exact"),
            dbc.NavLink("Area", href="/apps/area_chart", active="exact"),
        ],
        id="submenu-1-collapse",
    ),
]

submenu_reportes = [
    html.Li(
        "Reportes",
        style={"cursor": "pointer"},
        id="submenu-2",
    ),
    # we use the Collapse component to hide and reveal the navigation links
    dbc.Collapse(
        [
            dbc.NavLink("Generador Reportes", href="/apps/report_builder", active="exact"),
        ],
        id="submenu-2-collapse",
    ),
]


submenu_mapas = [
    html.Li(
        "Mapas",
        style={"cursor": "pointer"},
        id="submenu-3",
    ),
    # we use the Collapse component to hide and reveal the navigation links
    dbc.Collapse(
        [
            dbc.NavLink("Contorno y Estructural", href="/apps/contour_map", active="exact"),
            
        ],
        id="submenu-3-collapse",
    ),
]

submenu_datos = [
    html.Li(
        "Carga de Datos",
        style={"cursor": "pointer"},
        id="submenu-4",
    ),
    # we use the Collapse component to hide and reveal the navigation links
    dbc.Collapse(
        [
            dbc.NavLink("Eventos", href="/apps/events_loader", active="exact"),
            dbc.NavLink("Wellbore Diagram", href="/apps/wellbore_loader", active="exact"),
            dbc.NavLink("Survey", href="/apps/survey_loader", active="exact"),
            dbc.NavLink("Items", href="/apps/items_loader", active="exact"),
            dbc.NavLink("Puntos de Presión", href="/apps/mdt_loader", active="exact"),
            dbc.NavLink("Estratigráfia", href="/apps/markers_loader", active="exact"),
        ],
        id="submenu-4-collapse",
    ),
]

submenu_ingenieria = [
    html.Li(
        "Ingeniería",
        style={"cursor": "pointer"},
        id="submenu-5",
    ),
    # we use the Collapse component to hide and reveal the navigation links
    dbc.Collapse(
        [
            dbc.NavLink("Curva de Declinacion", href="/apps/decline_analysis", active="exact"),
            dbc.NavLink("Cross Section", href="/apps/cross_section", active="exact"),
            dbc.NavLink("Esquematico del Pozo", href="/apps/wellbore_diagram", active="exact"),
            dbc.NavLink("LAS", href="/apps/LAS_chart", active="exact"),
            dbc.NavLink("Python Interprete", href="/apps/python_interprete", active="exact"),
        ],
        id="submenu-5-collapse",
    ),
]

submenu_admin = [
    html.Li(
        # use Row and Col components to position the chevrons
        "Administración",
        style={"cursor": "pointer"},
        id="submenu-6",
    ),
    # we use the Collapse component to hide and reveal the navigation links
    dbc.Collapse(
        [
            dbc.NavLink("Variables Calculadas", href="/apps/variable_loader", active="exact"),    
            dbc.NavLink("SQL Builder", href="/apps/sql_builder2", active="exact"),
            dbc.NavLink("Actualizar BD", href="/apps/db_creation_update", active="exact"),
            dbc.NavLink("Exportar Datos", href="/apps/export_data", active="exact"),
            dbc.NavLink("Unidades", href="/apps/units_loader", active="exact"),
        ],
        id="submenu-6-collapse",
    ),
]


sidebar = html.Div(
    [
        dbc.Nav(submenu_graficos, vertical=True),
        dbc.Nav(submenu_reportes, vertical=True),
        dbc.Nav(submenu_mapas, vertical=True),
        dbc.Nav(submenu_datos, vertical=True),
        dbc.Nav(submenu_ingenieria, vertical=True),
        dbc.Nav(submenu_admin, vertical=True),
    ],
    id="sidebar",
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", children=[], style=CONTENT_STYLE)

app.layout = html.Div([
    dcc.Location(id="url"),
    dcc.Store(id='side_click'),
    navbar,
    sidebar,
    html.Div(content, style=dict(maxHeight=1200, overflowX='scroll')),
])

# this function is used to toggle the is_open property of each Collapse
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


# this function applies the "open" class to rotate the chevron
def set_navitem_class(is_open):
    if is_open:
        return "open"
    return ""

for i in [1, 2, 3, 4, 5, 6]:
    app.callback(
        Output(f"submenu-{i}-collapse", "is_open"),
        [Input(f"submenu-{i}", "n_clicks")],
        [State(f"submenu-{i}-collapse", "is_open")],
    )(toggle_collapse)

    app.callback(
        Output(f"submenu-{i}", "className"),
        [Input(f"submenu-{i}-collapse", "is_open")],
    )(set_navitem_class)

@app.callback(Output('page-content', 'children'),
              Output('screen_name', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/report_builder':
        return report_builder.layout, 'Generador de Reportes'
    if pathname == '/apps/multi_line_chart':
        return multi_line_chart.layout, 'Multi Grafico Línea'
    if pathname == '/apps/line_chart':
        return line_chart.layout, 'Gráfico de Línea'
    if pathname == '/apps/bar_chart':
        return bar_chart.layout, 'Gráfico de Barras'
    if pathname == '/apps/sunburst_chart':
        return sunburst_chart.layout, 'Graficos Sunburst'
    if pathname == '/apps/survey_loader':
        return survey_loader.layout, 'Cargador de Surveys'
    if pathname == '/apps/events_loader':
        return events_loader.layout, 'Cargador de eventos'
    if pathname == '/':
        return dashboard.layout, 'Dashboard'
    if pathname == '/apps/sql_builder2':
        return sql_builder2.layout, 'SQL Builder'
    if pathname == '/apps/decline_analysis':
        return decline_analysis.layout, 'Análisis de Declinación'
    if pathname == '/apps/contour_map': 
        return contour_map.layout, 'Mapas de Contorno'
    if pathname == '/apps/scatter_chart': 
        return scatter_chart.layout, 'Gráfico Scatter'
    if pathname == '/apps/area_chart': 
        return area_chart.layout, 'Gráfico de Área'
    if pathname == '/apps/wellbore_diagram': 
        return wellbore_diagram.layout, 'Diagrama Mecanico'
    if pathname == '/apps/wellbore_loader': 
        return wellbore_loader.layout, 'Cargador de Diagrama Mecánico'
    if pathname == '/apps/LAS_chart': 
        return LAS_chart.layout, 'Visualziador de Archivos LAS'
    if pathname == '/apps/cross_section': 
        return cross_section.layout, 'Generador de Cross Section'
    if pathname == '/apps/items_loader': 
        return items_loader.layout, 'Actualizacion Items'
    if pathname == '/apps/db_creation_update': 
        return db_creation_update.layout, 'Creación y Actualizacián de la BD'
    if pathname == '/apps/variable_loader': 
        return variable_loader.layout, 'Cargador de Variables Calculadas'
    if pathname == '/apps/python_interprete': 
        return python_interprete.layout, 'Interprete de Python'
    if pathname == '/apps/export_data': 
        return export_data.layout, 'Exportar Datos' 
    if pathname == '/apps/nodal': 
        return nodal.layout, 'Análisis Nodal'
    if pathname == '/apps/markers_loader': 
        return markers_loader.layout, 'Marcadores Estatigráficos'
    if pathname == '/apps/units_loader': 
        return units_loader.layout, 'Unidades'
    if pathname == '/apps/mdt_loader': 
        return mdt_loader.layout, 'Punto de Presión'     
        return None, 'Bye'
    else:
        return "404 Page Error! Please choose a link" , ""

webbrowser.open_new_tab('http://127.0.0.1:8050/')

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
   