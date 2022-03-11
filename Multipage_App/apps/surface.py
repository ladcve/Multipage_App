import dash_table
import configparser
import dash_html_components as html
import sqlite3
import os.path
import os
import json
import pandas as pd
from os import listdir
from os.path import isfile, join
import dash_daq as daq
import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Row import Row
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from datetime import datetime, tzinfo, timezone, timedelta, date
from dash_table.Format import Format, Symbol
import dash_admin_components as dac
import plotly.graph_objects as go

#z_data = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/api_docs/mt_bruno_elevation.csv')
z_data = pd.read_csv('./datasets/EMI5_CPS-3.csv')

print(z_data)

fig = go.Figure(data=[go.Surface(z=z_data.values)])

fig.update_layout(title='Mt Bruno Elevation', autosize=False,
                  width=1200, height=1200,
                  margin=dict(l=65, r=50, b=65, t=90))

fig.show()