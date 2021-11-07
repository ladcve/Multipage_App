import pandas as pd
import lasio

from plotly.subplots import make_subplots
import plotly.graph_objects as go

#https://medium.datadriveninvestor.com/the-best-library-to-plot-well-logs-with-python-70e9445f77f9
#https://github.com/abhishekdbihani/synthetic_well-log_polynomial_regression
#https://github.com/imranfadhil/logASCII_viewer
#https://towardsdatascience.com/displaying-lithology-data-using-python-and-matplotlib-58b4d251ee7a


las = lasio.LASFile("./datasets/8-32IN.LAS")
df = las.df()
df.head()
df.reset_index(inplace=True)
column_list = df.columns
column_list = column_list.drop(['DEPT'])

fig = make_subplots(rows=1, cols=len(column_list))
i=1
for columnas in column_list:
    fig.add_trace(
        go.Scatter(x=df[columnas],
            y=df['DEPT'],
            name=columnas),
            row=1, col=i,
    )
    i=i+1
    fig['layout']['yaxis']['autorange'] = "reversed"    

fig.update_xaxes(color="#FF0000",gridcolor="#000000")
fig.update_layout(height=1000, width=1600, title_text="LAS Visualization")
fig.show()