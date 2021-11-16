import lasio.examples
from plotly.subplots import make_subplots
import plotly.graph_objects as go

las = lasio.LASFile("./datasets/Perla-1X.LAS")
curves_lits = []
for curve in las.curves[1:]:
    curves_lits.append(curve.mnemonic)
print(curves_lits)
