# apps/homepage.py
from dash import html

layout = html.Div([
    html.H3('Homepage'),
    html.Div([
        html.Div([
            html.A(html.Img(src='/assets/house.png', style={'height': '300px', 'margin': '10px'}), href='/app2'),
            html.A("House", href='/app2', style={'display': 'block', 'textAlign': 'center'})
        ], style={'display': 'inline-block', 'width': '30%'}),
        html.Div([
            html.A(html.Img(src='/assets/City.png', style={'height': '300px', 'margin': '10px'}), href='/app2'),
            html.A("City", href='/app2', style={'display': 'block', 'textAlign': 'center'})
        ], style={'display': 'inline-block', 'width': '30%'}),
        html.Div([
            html.A(html.Img(src='/assets/room.png', style={'height': '300px', 'margin': '10px'}), href='/app2'),
            html.A("Room", href='/app2', style={'display': 'block', 'textAlign': 'center'})
        ], style={'display': 'inline-block', 'width': '30%'})
    ], style={'textAlign': 'center'})
])
