# index.py
from dash import html, dcc
from dash.dependencies import Input, Output

from app import app
import apps.homepage, apps.data_visualisation_house, apps.data_visualisation_room, apps.data_visualisation_city

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    try:
        if pathname == '/app1':
            return apps.homepage.layout
        elif pathname == '/app2':
            return apps.data_visualisation_house.layout
        elif pathname == '/app3':
            return apps.data_visualisation_city.layout
        elif pathname == '/app4':
            return apps.data_visualisation_room.layout
        else:
            return apps.homepage.layout  # default 'app1'
    except Exception as e:
        return html.Div([
            html.H3("Error"),
            html.P(str(e))
        ])


if __name__ == '__main__':
    app.run_server(debug=True)
