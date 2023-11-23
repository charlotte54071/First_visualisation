import dash
from dash import dcc, html
import plotly.graph_objects as go
import pandas as pd
from app import app

# Read data from the Excel file
try:
    df = pd.read_excel('dash_visu_export_room.xlsx', sheet_name='Sheet1')
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
        dcc.Link('Back to homepage', href='/homepage', style={'fontSize': 18, 'textAlign': 'center', 'family': 'Arial, '
                                                                                                               'sans'
                                                                                                               '-serif'}),
        # add back link
        html.Br(),  # add the change line
    ]),
    dcc.Graph(id='3d-mesh-plot-3',
              style={'display': 'flex',
                     'justifyContent': 'center',
                     'alignItems': 'center',
                     'height': '60vh'}),
    dcc.Graph(id='bar-chart-3'),
    dcc.Dropdown(
        id='cluster-dropdown-3',
        options=[{'label': f"Cluster {cluster}", 'value': cluster} for cluster in clusters],
        value=[clusters[0]],
        multi=True,
        clearable=False,
        style={'marginBottom': '24px'}
    ),
    html.Div(id='box-plots-container-3', style={'marginBottom': '60px'}),

    html.Div(children='Input your value', style={'height': '50px', 'fontSize': '24px', 'textAlign': 'center'}),
    html.Div([
        html.Div([
            html.Div(
                [
                    html.Label(param, style={'fontSize': '20px', 'marginRight': '15px'}),
                ], style={'width': '300px', 'display': 'inline-block', 'textAlign': 'right'}),
            dcc.Input(id=f'input-{param}', type='number', step='any', value=0 if not df.empty else 0,
                      style={'fontSize': '16px', 'width': '100px', 'display': 'inline-block'})
        ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '15px'})
        for param in parameters
    ], style={'textAlign': 'center', 'marginBottom': '20px'}),

    html.Button('Find Best Cluster', id='submit-button-3', style={'fontSize': '20px', 'lineHeight': '1.25'}),
    html.Div(id='best-cluster-output-3', style={'fontSize': '20px', 'textAlign': 'center'})

])


@app.callback(
    dash.dependencies.Output('3d-mesh-plot-3', 'figure'),
    [dash.dependencies.Input('3d-mesh-plot-3', 'relayoutData')]
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
    dash.dependencies.Output('bar-chart-3', 'figure'),
    [dash.dependencies.Input('cluster-dropdown-3', 'value')]
)
def update_bar_chart(selected_clusters):
    bar_data = []

    # 为每个指标分配一个颜色
    indicator_colors = {
        'UTCI': 'red',
        'GWP': 'green',
        'LCC': 'blue'
    }

    legend_added = {indicator: False for indicator in indicators}

    for cluster in normalized_avg_df.index:
        for indicator in indicators:
            # 当前指标的默认颜色
            show_legend = not legend_added[indicator]
            color = indicator_colors[indicator] if cluster in selected_clusters else 'rgba(204, 204, 204, 0.7)'
            bar_data.append(
                go.Bar(
                    x=[f"Cluster{cluster}"],
                    y=[normalized_avg_df.loc[cluster, indicator]],
                    name=indicator,
                    marker_color=color,
                    showlegend=show_legend
                )
            )
            legend_added[indicator] = True

    return {
        'data': bar_data,
        'layout': {
            'title': {'text': 'Einordnung der cluster',
                      'font':
                          {
                              'size': 24,
                              'color': 'black',
                              'family': 'Arial, sans-serif',
                              'weight': 'bold'
                          }},
            'xaxis': {'title': 'Cluster'},
            'yaxis': {
                'title': 'Ereignis der Aspekte',
                'tickvals': [0, 0.5, 1],
                'ticktext': ['Gut', 'Mittel', 'Schlecht']
            },
            'barmode': 'group',
            'bargap': 0.000001,
            'bargroupgap': 0.001,

        }
    }


@app.callback(
    [dash.dependencies.Output('box-plots-container-3', 'children'),
     dash.dependencies.Output('best-cluster-output-3', 'children')],
    [dash.dependencies.Input('cluster-dropdown-3', 'value'),
     dash.dependencies.Input('submit-button-3', 'n_clicks')],
    [dash.dependencies.State(f'input-{param}', 'value') for param in parameters]
)
def combined_callback(selected_clusters, n_clicks, *values):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    button_clicked = n_clicks and n_clicks > 0

    # Processing and normalizing user input
    input_values = {param: value for param, value in zip(parameters, values)}
    all_values_provided = all(value is not None for value in input_values.values())

    # Normalize user inputs or set to zero if not provided
    normalized_input_values = {param: (value - min_vals[param]) / (max_vals[param] - min_vals[param]) if value is not None else 0 for param, value in input_values.items()} if button_clicked else {}

    if trigger_id == 'submit-button' and button_clicked:
        if not all_values_provided or df.empty:
            return dash.no_update, "Please ensure all fields are filled before clicking 'Find Best Cluster'."

        differences = df[parameters].apply(lambda row: sum((row - pd.Series(input_values)) ** 2), axis=1)
        best_cluster = df.loc[differences.idxmin(), 'cluster']
        best_cluster_output = f'The most suitable cluster for the given parameters is: Cluster {best_cluster}'
    else:
        best_cluster_output = dash.no_update

    # Update Box Plot chart
    filtered_df = df_normalized[df['cluster'].isin(selected_clusters)]
    traces = []
    for parameter in parameters:
        traces.append(go.Box(y=filtered_df[parameter], name=parameter, boxpoints='all', jitter=0.3, pointpos=-1.8))
        # Add red dots to denote the normalized values of user input if the submit button has been clicked at least once
        if button_clicked:
            user_input_normalized = normalized_input_values.get(parameter, 0)
            traces.append(go.Scatter(x=[parameter], y=[user_input_normalized], mode='markers', marker=dict(color='red', size=10)))

    box_plot = dcc.Graph(
        figure={
            'data': traces,
            'layout': go.Layout(
                title=dict(text="Box Plots for Selected Clusters",
                           font={'size': 24, 'color': "black", 'family': "Arial, sans-serif"}),
                yaxis=dict(title="Normalized Value", tickvals=[0, 0.5, 1], ticktext=['Low', 'Medium', 'High']),
                xaxis=dict(title="Parameters"),
                showlegend=False,
                margin=dict(l=80, r=40, t=40, b=120),  # Fixed margins
                height=600,  # Fixed height
                width=1500  # Fixed width
            )
        }
    )
    return box_plot, best_cluster_output






