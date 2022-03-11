import pandas as pd
import plotly.express as px

event_dates = ['2020-01-01', '2020-02-01', '2020-03-01',
               '2020-04-01', '2020-05-01', '2020-06-01', 
               '2020-07-01', '2020-08-01', '2020-09-01', 
               '2020-10-01', '2020-01-01', '2020-02-01', 
               '2020-03-01', '2020-04-01', '2020-05-01', 
               '2020-06-01', '2020-07-01', '2020-08-01', 
               '2020-09-01', '2020-10-01']
groupid = ['A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A',
           'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B']
outcome = [92,  93, 107,  91, 113,  83,  87,  99, 101, 107, 
           103, 145, 131, 116, 131, 109, 108, 105,  96, 127]
data = {'event_date': event_dates,
        'groupid': groupid,
        'outcome': outcome}
# create the dataframe from the arrays
df = pd.DataFrame(data)

fig = px.line(
    df
    , x='event_date'
    , y='outcome'
    , title = "Event Data Over Time for Two Groups"
    , color="groupid"
    , range_x=['2019-12-01', '2020-11-01'],
)
fig.update_layout(
    autosize=False,
    width=800,
    height=600,)
fig.add_annotation(
    x='2020-03-21'
    , y=145+1
    , text=f'Mar 21<br>First day of spring'
    , yanchor='bottom'
    , showarrow=False
    , arrowhead=1
    , arrowsize=1
    , arrowwidth=2
    , arrowcolor="#636363"
    , ax=-20
    , ay=-30
    , font=dict(size=12, color="orange", family="Sans Serif")
    , align="left"
    ,)
fig.add_annotation(
    x='2020-06-07'
    , y=145+1
    , text=f'Jun 21<br>First day<br>of summer'
    , yanchor='bottom'
    , showarrow=False
    , arrowhead=1
    , arrowsize=1
    , arrowwidth=2
    , arrowcolor="#636363"
    , ax=-20
    , ay=-30
    , font=dict(size=12, color="purple", family="Sans Serif")
    , align="left"
    ,)
# add vertical lines
fig.update_layout(shapes=
                  [dict(type= 'line',
                        yref= 'paper', y0= 0, y1= 1,
                        xref= 'x', x0='2020-03-21', x1='2020-03-21',
                        line=dict(color="MediumPurple",
                                  width=3,
                                  dash="dot")
                        ),
                  dict(type= 'line',
                        yref= 'paper', y0= 0, y1= 1,
                        xref= 'x', x0='2020-06-21', x1='2020-06-21',
                        line=dict(color="MediumPurple",
                                  width=3,
                                  dash="solid")
                       )
                  ])
# In United States: 'unofficial' summer is from Memorial Day to Labor Day
# Make a vertical highlight section
fig.add_vrect(x0="2020-05-25", x1="2020-09-07", 
              annotation_text="Unofficial<br>Summertime<br>in USA<br>(Memorial Day to<br>Labor Day)", annotation_position="top right",  
              annotation_font_size=11,
              annotation_font_color="Green",
              fillcolor="yellow", opacity=0.25, line_width=0)
# Make a horizontal highlight section
fig.add_hrect(y0=90, y1=100, 
              annotation_text="Observed data<br>of interest", annotation_position="top right",  
              annotation_font_size=11,
              annotation_font_color="Black",
              fillcolor="red", opacity=0.25, line_width=0)
fig.show()