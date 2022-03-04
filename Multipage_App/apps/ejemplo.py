import plotly.express as px
from skimage import io
img = io.imread('D:/Proyectos/Prod_Analysis/pictures/Perla-10.PNG')
fig = px.imshow(img)
fig.update_layout(coloraxis_showscale=False)
fig.update_xaxes(showticklabels=False)
fig.update_yaxes(showticklabels=False)
fig.show()