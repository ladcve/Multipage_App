import plotly.graph_objs as go
import pandas as pd
# added State to be used in callbacks
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash_table.Format import Format, Symbol
import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Row import Row

# using #type: ignore to suppress warnings in my editor (vs code). 
df = pd.read_excel("https://github.com/chris1610/pbpython/blob/master/data/salesfunnel.xlsx?raw=True")
pv = pd.pivot_table(df, index=['Name'], columns=["Status"], values=['Quantity'], aggfunc=sum, fill_value=0)#type: ignore

trace1 = go.Bar(x=pv.index, y=pv[('Quantity', 'declined')], name='Declined') #type: ignore
trace2 = go.Bar(x=pv.index, y=pv[('Quantity', 'pending')], name='Pending')#type: ignore
trace3 = go.Bar(x=pv.index, y=pv[('Quantity', 'presented')], name='Presented')#type: ignore
trace4 = go.Bar(x=pv.index, y=pv[('Quantity', 'won')], name='Won')#type: ignore

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(children=[
    html.H1(children='Sales Funnel Report'),
    html.Div(children='''National Sales Funnel Report.'''),
    dcc.Graph(
        id='graph',
        figure={
            'data': [trace1, trace2, trace3, trace4],
            'layout':
                go.Layout(title='Order Status by Customer', barmode='stack')#type: ignore
        }),
    dbc.Button("toggle", id="open"),
    dbc.Modal(
        [
            dbc.ModalHeader("Header",id = 'modalheader'),
            dbc.ModalBody("This is the content of the modal"),
            dbc.ModalFooter(
                dbc.Button("Close", id="close", className="ml-auto")
            ),
        ],
        size="xl",
        id="modal",
    )
])

@app.callback([Output("modal", "children"),
               Output("modal", "is_open")],
              [Input("graph", "clickData"),
               Input("close", "n_clicks")],
              [State("modal", "is_open"),
               State("modal", "children")])
def set_content(value,clicked,is_open,children):
    ctx = dash.callback_context

    if ctx.triggered[0]['prop_id'] == 'close.n_clicks':
        # you pressed the closed button, keeping the modal children as is, and 
        # close the model itself. 
        return children, False 
    elif ctx.triggered[0]['prop_id'] == 'graph.clickData':
        # you clicked in the graph, returning the modal children and opening it
        return [dbc.ModalHeader("Test"),
                dbc.ModalBody(
                html.Div([
                    html.Div([
                        html.H6('Sales', style={'textAlign': 'center', 'padding': 10}),
                        html.P("Bitch", id="sales_stocks", style={'textAlign': 'center', 'padding': 10})
                    ], className='pretty_container four columns'),
                    html.Div([
                        html.H5('Current ratio', style={'textAlign': 'center', 'padding': 10}),
                        html.P(str(value),style = {'fontFamily':'monospace'})
                    ], className='pretty_container seven columns')
                ])),
                dbc.ModalFooter(dbc.Button("Close", id="close"))
                ], True
    else:
        raise dash.exceptions.PreventUpdate

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run_server(debug=False)