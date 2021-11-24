import dash
import dash_ace
import dash_html_components as html
import flask
from flask import jsonify


app = dash.Dash(__name__,
                routes_pathname_prefix='/dash/'
                )

app.layout = html.Div([
    dash_ace.DashAceEditor(
        id='input',
        value='def test(a: int) -> str : \n'
              '    return f"value is {a}"',
        theme='github',
        mode='python',
        tabSize=2,
        enableBasicAutocompletion=True,
        enableLiveAutocompletion=True,
        autocompleter='/autocompleter?prefix=',
        placeholder='Python code ...'
    )
])

def autocompleter():
    return jsonify([{"name": "Completed", "value": "Completed", "score": 100, "meta": "test"}])


if __name__ == '__main__':
    app.run_server(debug=False)