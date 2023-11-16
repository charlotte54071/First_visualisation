import dash
from dash import dcc, html
import plotly.graph_objects as go
import pandas as pd
from app import app

# Read data from the Excel file
try:
    df = pd.read_excel('dash_visu_export.xlsx', sheet_name='Sheet1')
    if not all(column in df.columns for column in ['UTCI', 'GWP', 'LCC', 'cluster']):
        raise ValueError("Some essential columns are missing from the Excel sheet.")
except Exception as e:
    print(f"Error reading the Excel file: {e}")
    df = pd.DataFrame()

# For Bar Chart
indicators = ['UTCI', 'GWP', 'LCC']
avg_df = df.groupby('cluster').mean()

max_values = df[indicators].max()
min_values = df[indicators].min()


def normalize(column):
    return (column - min_values[column.name]) / (max_values[column.name] - min_values[column.name])


normalized_avg_df = avg_df[indicators].apply(normalize)

# For Box Plot
parameters = [
    "Baumanteil [%]", "PV-Dach [%]", "PV battery capacity", "PV-facade-% south",
    "Fensterflächenanteil", "Fenster g-Wert", "Gründachstärke",
    "Kronendurchmesser", "Baumhöhe", "Kronentransparenz Sommer",
    "Kronentransparenz Winter", "Albedo Fassade", "Straßenbreite", "PV Ost-West Fassade [%]"
]

min_vals = df[parameters].min()
max_vals = df[parameters].max()
df_normalized = (df[parameters] - min_vals) / (max_vals - min_vals)
clusters = sorted(df['cluster'].unique())

layout = html.Div([
    html.Div([
        dcc.Link('Back to homepage', href='/app1', style={'fontSize': 18, 'textAlign': 'center', 'family': 'Arial, '
                                                                                                           'sans-serif'}),
        # add back link
        html.Br(),  # add the change line
    ]),
    dcc.Graph(id='3d-mesh-plot',
              style={'display': 'flex',
                     'justifyContent': 'center',
                     'alignItems': 'center',
                     'height': '60vh'}),
    dcc.Graph(
        id='bar-chart',
        figure={
            'data': [
                {'x': normalized_avg_df.index, 'y': normalized_avg_df['UTCI'], 'type': 'bar', 'name': 'UTCI'},
                {'x': normalized_avg_df.index, 'y': normalized_avg_df['GWP'], 'type': 'bar', 'name': 'GWP'},
                {'x': normalized_avg_df.index, 'y': normalized_avg_df['LCC'], 'type': 'bar', 'name': 'LCC'}
            ],
            'layout': {
                'title':
                    {
                        'text': 'Einordnung der cluster',
                        'font':
                            {
                                'size': 24,
                                'color': 'black',
                                'family': 'Arial, sans-serif',
                                'weight': 'bold',
                            }
                    },
                'xaxis': {
                    'title': 'Clusternummer'
                },
                'yaxis': {
                    'title': 'Ereignis der Aspekte',
                    'tickvals': [0, 0.5, 1],
                    'ticktext': ['Gut', 'Mittel', 'Schlecht']
                }
            }
        }
    ),

    dcc.Dropdown(
        id='cluster-dropdown',
        options=[{'label': f"Cluster {cluster}", 'value': cluster} for cluster in clusters],
        value=clusters[0],
        clearable=False
    ),

    dcc.Graph(id='box-plot', style={'marginBottom': '60px'}),

    html.Div(children='Input your value', style={'height': '50px', 'fontSize': '24px', 'textAlign': 'center'}),
    html.Div([
        html.Div([
            html.Div([
                html.Label(param, style={'fontSize': '20px', 'marginRight': '15px'}),
            ], style={'width': '300px', 'display': 'inline-block', 'textAlign': 'right'}),
            dcc.Input(id=f'input-{param}', type='number', step='any', value=0 if not df.empty else 0,
                      style={'fontSize': '16px', 'width': '100px', 'display': 'inline-block'})
        ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '15px'})
        for param in parameters
    ], style={'textAlign': 'center', 'marginBottom': '20px'}),

    html.Button('Find Best Cluster', id='submit-button', style={'fontSize': '20px', 'lineHeight': '1.25'}),
    html.Div(id='best-cluster-output', style={'fontSize': '20px', 'textAlign': 'center'})

])


@app.callback(
    dash.dependencies.Output('3d-mesh-plot', 'figure'),
    [dash.dependencies.Input('3d-mesh-plot', 'relayoutData')]
)
def update_3d_mesh_plot(relayoutData):
    if df.empty:
        return {}

    x = df['UTCI']
    y = df['GWP']
    z = df['LCC']

    # assign color according to the value of x, y, z
    max_x, max_y, max_z = max(x), max(y), max(z)
    colors = []

    for i, j, k in zip(x, y, z):
        r_ratio = i / max_x
        g_ratio = j / max_y
        b_ratio = k / max_z

        rgb_color = (int(0 * r_ratio), int(101 * g_ratio), int(189 * b_ratio))
        colors.append(f'rgb{rgb_color}')

    # create mesh 3d
    mesh = go.Mesh3d(x=x, y=y, z=z, colorbar_title='intensity', vertexcolor=colors, opacity=0.7, colorscale=None)

    layout = go.Layout(
        scene=dict(aspectmode="cube"),
        title={
            'text': 'Handlungsspielraum',
            'y': 0.9,  # define the 'y' coordinate of title
            'x': 0.5,  # in the middle
            'xanchor': 'center',
            'yanchor': 'top',

        }
    )

    # title of x,y,z
    layout.scene.xaxis.title = 'UTCI'
    layout.scene.yaxis.title = 'GWP'
    layout.scene.zaxis.title = 'LCC'

    fig = go.Figure(data=[mesh], layout=layout)

    fig.update_layout(
        title=dict(text='Handlungsspielraum',
                   font=dict(size=24,
                             color='black',
                             family='Arial, sans-serif',
                             )

                   )
    )

    return fig


@app.callback(
    dash.dependencies.Output('box-plot', 'figure'),
    [dash.dependencies.Input('cluster-dropdown', 'value')]
)
def update_box_plot(selected_cluster):
    traces = []

    for parameter in parameters:
        traces.append(
            go.Scatter(
                x=[parameter, parameter],
                y=[0, 1],
                mode='lines',
                line=dict(color='lightgrey', width=1),
                showlegend=False
            )
        )

    cluster_df = df_normalized[df['cluster'] == selected_cluster]

    for parameter in parameters:
        traces.append(
            go.Box(
                y=cluster_df[parameter],
                name=parameter,
                boxpoints='all',
                jitter=0.3,
                pointpos=-1.8,
                showlegend=False
            )
        )

    return {
        'data': traces,
        'layout': go.Layout(
            title=dict(text=f"Box plots for Cluster {selected_cluster}", font=dict(size=24,
                                                                                   color='black',
                                                                                   family='Arial, sans-serif',
                                                                                   )),
            yaxis=dict(title="Value", tickvals=[0, 0.5, 1], ticktext=['Niedrig', 'Mittel', 'Hoch'])
        )
    }


@app.callback(
    dash.dependencies.Output('best-cluster-output', 'children'),
    [dash.dependencies.Input('submit-button', 'n_clicks')],  # only care about the button
    [dash.dependencies.State(f'input-{param}', 'value') for param in parameters]
    # Use State to get the current value of an input field without triggering a callback
)
def find_best_cluster(n_clicks, *values):
    # If the button has not been clicked, or the data frame is empty, no calculation is performed.
    if n_clicks is None or df.empty:
        return "Please enter the values and click 'Find Best Cluster'."

    input_values = {param: value for param, value in zip(parameters, values)}

    if any(value is None for value in input_values.values()):
        return "Please make sure all fields are filled before clicking 'Find Best Cluster'."

    differences = df[parameters].apply(lambda row: sum((row - pd.Series(input_values)) ** 2), axis=1)
    best_cluster = df.loc[differences.idxmin(), 'cluster']

    return f'The most suitable cluster for the given parameters is: Cluster {best_cluster}'
