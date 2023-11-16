import dash
from dash import dcc, html
import plotly.graph_objects as go
import pandas as pd

# Initialize the Dash app
app = dash.Dash(__name__)

# Read data from the Excel file
df = pd.read_excel('dash_visu_export.xlsx', sheet_name='Sheet1')

# Check if 'cluster' column is present in the dataframe
if 'cluster' not in df.columns:
    raise ValueError("'cluster' column not found in the dataframe.")

# Parameters
parameters = [
    "Baumanteil [%]", "PV-Dach [%]", "PV battery capacity", "PV-facade-% south",
    "Fensterflächenanteil", "Fenster g-Wert", "Gründachstärke",
    "Kronendurchmesser", "Baumhöhe", "Kronentransparenz Sommer",
    "Kronentransparenz Winter", "Albedo Fassade", "Straßenbreite", "PV Ost-West Fassade [%]"
]

# Normalize the values
min_vals = df[parameters].min()
max_vals = df[parameters].max()
df_normalized = (df[parameters] - min_vals) / (max_vals - min_vals)

clusters = sorted(df['cluster'].unique())

# App layout
app.layout = html.Div([
    dcc.Dropdown(
        id='cluster-dropdown',
        options=[{'label': f"Cluster {cluster}", 'value': cluster} for cluster in clusters],
        value=clusters[0],
        clearable=False
    ),
    dcc.Graph(id='box-plot')
])

@app.callback(
    dash.dependencies.Output('box-plot', 'figure'),
    [dash.dependencies.Input('cluster-dropdown', 'value')]
)
def update_box_plot(selected_cluster):
    traces = []

    # Adding the reference lines first
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
        median_value = cluster_df[parameter].median()
        traces.append(
            go.Box(
                y=cluster_df[parameter],
                name=parameter,
                boxpoints='all',
                jitter=0.3,
                pointpos=-1.8,
            )
        )
        traces.append(
            go.Scatter(
                y=[median_value],
                mode='markers',
                marker=dict(color='red', size=10),
                x=[parameter],
                showlegend=False,
                name=f'Median of {parameter}'
            )
        )

    return {
        'data': traces,
        'layout': go.Layout(
            title=f"Box plots for Cluster {selected_cluster}",
            yaxis=dict(title="Value", tickvals=[0, 0.5, 1], ticktext=['Niedrig', 'Mittel', 'Hoch'])
        )
    }



if __name__ == '__main__':
    app.run_server(debug=True)