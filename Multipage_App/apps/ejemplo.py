import dash_player
from textwrap import dedent
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State

app = dash.Dash(__name__)

app.scripts.config.serve_locally = True


app.layout = html.Div([
    dash_player.DashPlayer(
        id='video-player',
        url='https://media.w3.org/2010/05/sintel/trailer.webm',
        controls=True
    ),

    html.Button('Set seekTo to 10', id='button-seek-to'),

    html.Div(id='div-current-time', style={'margin-bottom': '20px'}),

    html.Div(id='div-method-output'),

    dcc.Markdown(dedent('''
            ### Video Examples
            * mp4: http://media.w3.org/2010/05/bunny/movie.mp4
            * mp3: https://media.w3.org/2010/07/bunny/04-Death_Becomes_Fur.mp3
            * webm: https://media.w3.org/2010/05/sintel/trailer.webm
            * ogv: http://media.w3.org/2010/05/bunny/movie.ogv
            * Youtube: https://www.youtube.com/watch?v=sea2K4AuPOk
            '''))
])


@app.callback(Output('div-current-time', 'children'),
              [Input('video-player', 'currentTime')])
def update_time(currentTime):
    return 'Current Time: {}'.format(currentTime)


@app.callback(Output('div-method-output', 'children'),
              [Input('video-player', 'secondsLoaded')],
              [State('video-player', 'duration')])
def update_methods(secondsLoaded, duration):
    return 'Second Loaded: {}, Duration: {}'.format(secondsLoaded, duration)


@app.callback(Output('video-player', 'seekTo'),
              [Input('button-seek-to', 'n_clicks')])
def set_seekTo(n_clicks):
    return 10


if __name__ == '__main__':
    app.run_server(debug=False)


    import dash
from dash import html
