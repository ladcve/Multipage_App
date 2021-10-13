# importing modules
from matplotlib import pyplot as plt    # plotting
import numpy as np                      # numerical array
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input, State
import dash_bootstrap_components as dbc
from app import app

# Undersaturated Oil Reservoir
### Known data ###
# Reservoir
P_res   = 5500.0  # Reservoir Pressure [psia]
P_bp    = 3000.0  # Bubble Point Pressure [psia]

# Tested Data
# Well A
P_wfAt  = 4000.0  # Tested flowing bottom-hole pressure in Well A [psia]
q_At    = 300.0   # Tested production rate from Well A [psia]

# Well B
P_wfBt  = 2000.0  # Tested flowing bottom-hole pressure in Well B [psia]
q_Bt    = 900.0   # Tested production rate from Well B [psia]

# Construct IPR using generalized Vogel method

### Calculation and Plotting ###
# Well A
# Tested flowing bottom-hole pressure in Well A 
# bigger than Bubble Point Pressure
J_A = q_At / (P_res - P_wfAt)   # Productivity Index Well A [STB/(day.psia)]
q_vA = J_A * P_bp / 1.8         # [STB/day]
q_bA = J_A * (P_res - P_bp)     # [STB/day]

# Well B
# Tested flowing bottom-hole pressure in Well B 
# lower than Bubble Point Pressure

# Productivity Index Well B [STB/(day.psia)]  J_B
J_B = q_Bt/((P_res-P_bp)+(P_bp/1.8)*(1-0.2*(P_wfBt/P_bp)-0.8*(P_wfBt/P_bp)**2))
q_vB = J_B * P_bp / 1.8          # [STB/day]
q_bB = J_B * (P_res - P_bp)      # [STB/day]


## Equation to calculate q in Well A and Well B
# Equation for P_wf <= P_bp
def q_bBHP(P_wf, q_v, q_b):
    return q_b + q_v * ( 1 - 0.2*(P_wf/P_bp) - 0.8*(P_wf/P_bp)**2)

# Equation for P_wf > P_bp
def q_uBHP(P_wf, J):
    return J * (P_res - P_wf)

# Generate bottom-hole pressure dataset for calculated points
P_wf = np.arange(0, 5500.05, 0.05) # 110001 dataset [0, 0.05, ..., 5500]
#print len(P_wf)
# Separate the dataset
x1 = P_wf[P_wf < 3000]     # P_wf <= 3000 psia
x2 = P_wf[P_wf >= 3000]    # P_wf > 3000 psia

# Calculating q for each dataset in Well A and Well B
y1A = q_bBHP(x1, q_vA, q_bA)    # q_A for P_wf <= 3000 psia
y2A = q_uBHP(x2, J_A)           # q_A for P_wf > 3000 psia
y1B = q_bBHP(x1, q_vB, q_bB)    # q_B for P_wf <= 3000 psia
y2B = q_uBHP(x2, J_B)           # q_B for P_wf > 3000 psia

# Point each step in 500
x1p  = x1[::10000]
x2p  = x2[::10000]
y1Ap = y1A[::10000]
y2Ap = y2A[::10000]
y1Bp = y1B[::10000]
y2Bp = y2B[::10000]

# Layout section: Bootstrap (https://hackerthemes.com/bootstrap-cheatsheet/)
# ************************************************************************
layout = dbc.Container([

    dbc.Row(
        dbc.Col(html.H1("Well A IPR Curve",
                        className='text-center text-primary mb-4'),
                width=12)
    ),

    dbc.Row([

        dbc.Col([ dcc.Graph(id='line-fig', figure={})
        ],# width={'size':5, 'offset':1, 'order':1},
           xs=12, sm=12, md=12, lg=5, xl=5
        ),

        dbc.Col([
            dcc.Dropdown(id='my-dpdn2', multi=True, value=['PFE','BNTX'],
                         options=[{'label':x, 'value':x}
                                  for x in sorted(df['Symbols'].unique())],
                         ),
            dcc.Graph(id='line-fig2', figure={})
        ], #width={'size':5, 'offset':0, 'order':2},
           xs=12, sm=12, md=12, lg=5, xl=5
        ),

    ], no_gutters=True, justify='start'),  # Horizontal:start,center,end,between,around

    dbc.Row([
        dbc.Col([ dcc.Graph(id='my-hist', figure={}),
        ], #width={'size':5, 'offset':1},
           xs=12, sm=12, md=12, lg=5, xl=5
        ),

        dbc.Col([
            dbc.Card(
                [
                    dbc.CardBody(
                        html.P(
                            "We're better together. Help each other out!",
                            className="card-text")
                    ),
                    dbc.CardImg(
                        src="https://media.giphy.com/media/Ll0jnPa6IS8eI/giphy.gif",
                        bottom=True),
                ],
                style={"width": "24rem"},
            )
        ], #width={'size':5, 'offset':1},
           xs=12, sm=12, md=12, lg=5, xl=5
        )
    ], align="center")  # Vertical: start, center, end

], fluid=True)


# Plotting IPR Curve
# Well A IPR Curve
plt.figure()
plt.grid()
plt.title('Inflow Performance Relationship for Well A')
plt.plot(y1A, x1, y2A, x2, y1Ap, x1p, 'ro', y2Ap, x2p, 'ro',  y2A[0], x2[0], 'r*')
plt.vlines(y2A[0], 0, x2[0], linestyles='dashed')
plt.hlines(x2[0], 0, y2A[0], linestyles='dashed')
plt.xlabel('Oil Production Rate q(stb/day)')
plt.ylabel('Bottom-Hole Pressure p_wf(psia)')
ps = 'q ; p_wf = p_b'
plt.annotate(ps, xy=(y2A[0],x2[0]), xycoords='data', xytext=(200, 90),
             textcoords='offset points',
             arrowprops=dict(facecolor='black', shrink=0.05, width=1),
             horizontalalignment='right', verticalalignment='top')
plt.legend(('q ; p_wf < 3000 psi', 'q ; p_wf >= 3000 psi'),
           'upper right', shadow=True)

# Well B IPR Curve
plt.figure()
plt.grid()
plt.title('Inflow Performance Relationship for Well B')
plt.plot(y1B, x1, y2B, x2, y1Bp, x1p, 'ro', y2Bp, x2p, 'ro', y2B[0], x2[0], 'r*')
plt.vlines(y2B[0], 0, x2[0], linestyles='dashed')
plt.hlines(x2[0], 0, y2B[0], linestyles='dashed')
plt.xlabel('Oil Production Rate q(stb/day)')
plt.ylabel('Bottom-Hole Pressure p_wf(psia)')
ps = 'q ; p_wf = p_b'
plt.annotate(ps, xy=(y2B[0],x2[0]), xycoords='data', xytext=(200, 90),
             textcoords='offset points',
             arrowprops=dict(facecolor='black', shrink=0.05, width=1),
             horizontalalignment='right', verticalalignment='top')
plt.legend(('q ; p_wf < 3000 psi', 'q ; p_wf >= 3000 psi'),
           'upper right', shadow=True)

# Comparison between Well A and B
yA = y1A.tolist() + y2A.tolist()
yB = y1B.tolist() + y2B.tolist()
plt.figure()
plt.grid()
plt.title('IPR Comparison Between Well A and Well B')
plt.plot(yA, P_wf, 'b', yB, P_wf, 'g')
plt.legend(('Well A', 'Well B'),
           'upper right', shadow=True)
plt.xlabel('Oil Production Rate q(stb/day)')
plt.ylabel('Bottom-Hole Pressure p_wf(psia)')

plt.show()