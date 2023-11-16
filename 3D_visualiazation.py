import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

# read file
try:
    df = pd.read_excel('dash_visu_export.xlsx', sheet_name='Sheet1')
    columns = df.columns
    if not all(column in columns for column in ['UTCI', 'GWP', 'LCC']):
        raise ValueError("Some columns are missing from the Excel sheet.")
except Exception as e:
    print(f"Error reading the Excel file: {e}")
    df = pd.DataFrame()

# Create Dash app
app = dash.Dash(__name__)

# define layout
app.layout = html.Div([
    dcc.Graph(id='3d-plot',style={'width': '800px', 'height': '600px'})
])

@app.callback(
    Output('3d-plot', 'figure'),
    [Input('3d-plot', 'relayoutData')]
)
def update_3d_plot(relayoutData):
    if df.empty:
        return {}

    x = df['UTCI']
    y = df['GWP']
    z = df['LCC']


    fig = px.scatter_3d(df, x=x, y=y, z=z, color=z, opacity=0.9)
    fig.update_traces(marker=dict(size=8),
                      selector=dict(mode='markers+lines'))



    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
