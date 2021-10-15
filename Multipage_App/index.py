import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import base64
import datetime

# Connect to main app.py file
from app import app

# Connect to your app pages
from apps import report_builder, line_chart, bar_chart, pie_chart, events_loader, survey_loader, dashboard, sql_builder

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
                ],
                align="center",
                no_gutters=True,
            ),
        ),
    ],
    color="dark",
    dark=True,
)

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 60,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#133c65",
}


SIDEBAR_HIDEN = {
    "position": "fixed",
    "top": 52,
    "left": "-16rem",
    "bottom": 0,
    "width": "16rem",
    "height": "100%",
    "z-index": 1,
    "overflow-x": "hidden",
    "transition": "all 0.5s",
    "padding": "0rem 0rem",
    "background-color": "#f8f9fa",
}

# padding for the page content
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/", active="exact"),
                dbc.NavLink("Generador Reportes", href="/apps/report_builder", active="exact"),
                dbc.NavLink("Gráfico Línea", href="/apps/line_chart", active="exact"),
                dbc.NavLink("Gráfico Barras", href="/apps/bar_chart", active="exact"),
                dbc.NavLink("Gráfico Torta", href="/apps/pie_chart", active="exact"),
                dbc.NavLink("Datos de Eventos", href="/apps/events_loader", active="exact"),
                dbc.NavLink("Datos de Eventos", href="/apps/survey_loader", active="exact"),
                dbc.NavLink("Ingenieria", href="/apps/live_bootstrap", active="exact"),
                dbc.NavLink("Variables Calculadas", href="/apps/live_bootstrap", active="exact"),    
                dbc.NavLink("SQL Builder", href="/apps/sql_builder", active="exact"),          
            ],
            vertical=True,
            pills=True,
        ),
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
    html.Div(content, style=dict(maxHeight=720, overflowX='scroll')),
])

@app.callback(
    [
        Output("sidebar", "style"),
        Output("page-content", "style"),
        Output("side_click", "data"),
    ],

    [Input("btn_sidebar", "n_clicks")],
    [
        State("side_click", "data"),
    ]
)
def toggle_sidebar(n, nclick):
    if n:
        if nclick == "SHOW":
            sidebar_style = SIDEBAR_HIDEN
            content_style = CONTENT_STYLE
            cur_nclick = "HIDDEN"
        else:
            sidebar_style = SIDEBAR_STYLE
            content_style = CONTENT_STYLE
            cur_nclick = "SHOW"
    else:
        sidebar_style = SIDEBAR_STYLE
        content_style = CONTENT_STYLE
        cur_nclick = 'SHOW'

    return sidebar_style, content_style, cur_nclick

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/report_builder':
        return report_builder.layout
    if pathname == '/apps/line_chart':
        return line_chart.layout
    if pathname == '/apps/bar_chart':
        return bar_chart.layout
    if pathname == '/apps/pie_chart':
        return pie_chart.layout
    if pathname == '/apps/survey_loader':
        return survey_loader.layout
    if pathname == '/apps/events_loader':
        return events_loader.layout
    if pathname == '/':
        return dashboard.layout
    if pathname == '/apps/sql_builder':
        return sql_builder.layout
    else:
        return "404 Page Error! Please choose a link"


if __name__ == '__main__':
    app.run_server(debug=True)