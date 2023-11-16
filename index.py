# index.py
from dash import html, dcc
from dash.dependencies import Input, Output

from app import app
import apps.app1, apps.app2  # 引入app1和app2

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    try:
        if pathname == '/app1':
            return apps.app1.layout
        elif pathname == '/app2':
            return apps.app2.layout
        else:
            return apps.app1.layout  # default 'app1'
    except Exception as e:
        return html.Div([
            html.H3("Error"),
            html.P(str(e))
        ])


if __name__ == '__main__':
    app.run_server(debug=True)
