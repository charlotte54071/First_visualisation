import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd

# 读取Excel文件中的数据
df = pd.read_excel('dash_visu_export.xlsx', sheet_name='Sheet1')

# 检查数据框中是否存在'cluster'列
if 'cluster' not in df.columns:
    raise ValueError("'cluster' column not found in the dataframe.")

# 标准化指标
indicators = ['UTCI', 'GWP', 'LCC']
max_values = df[indicators].max()
min_values = df[indicators].min()
avg_df = df.groupby('cluster').mean()


def normalize(column):
    return (column - min_values[column.name]) / (max_values[column.name] - min_values[column.name])


normalized_avg_df = avg_df[indicators].apply(normalize)

# 盒形图的参数
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

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Graph(id='bar-chart'),
    dcc.Dropdown(
        id='cluster-dropdown',
        options=[{'label': f"Cluster {cluster}", 'value': cluster} for cluster in clusters],
        value=[clusters[0]],
        multi=True,
        clearable=False
    ),
    html.Div(id='box-plots-container',style={'marginBottom': '60px'})
])


@app.callback(
    Output('bar-chart', 'figure'),
    [Input('cluster-dropdown', 'value')]
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
            'title': 'Normalized Cluster Averages',
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
    Output('box-plots-container', 'children'),
    [Input('cluster-dropdown', 'value')]
)
def update_box_plots(selected_clusters):
    filtered_df = df_normalized[df['cluster'].isin(selected_clusters)]
    traces = [go.Box(y=filtered_df[parameter], name=parameter, boxpoints='all', jitter=0.3, pointpos=-1.8) for parameter
              in parameters]

    return dcc.Graph(
        figure={
            'data': traces,
            'layout': go.Layout(
                title="Box Plots for Selected Clusters",
                yaxis=dict(title="Normalized Value", tickvals=[0, 0.5, 1], ticktext=['Low', 'Medium', 'High']),
                xaxis=dict(title="Parameters")
            )
        }
    )


if __name__ == '__main__':
    app.run_server(debug=True)
