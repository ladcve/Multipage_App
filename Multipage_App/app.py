import dash
import dash_bootstrap_components  as dbc

FONT_AWESOME = "https://use.fontawesome.com/releases/v5.7.2/css/all.css"



# meta_tags are required for the app layout to be mobile responsive
app = dash.Dash(__name__, title="Prod Analysis", suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP, FONT_AWESOME],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}],
                )
# styling the sidebar
server = app.server