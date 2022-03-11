import os
import dash
import dash_html_components as html

app = dash.Dash(__name__)

app.layout = html.Div(children = [
        html.Video(
            controls = False,
            id = 'movie_player',
            src = "C:/Users/lduarte/Videos/Captures/acceso_sistema.mp4",
            autoPlay=True
        ),
    ])

if __name__ == '__main__':
    app.run_server(debug=False)