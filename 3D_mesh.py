import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go

# 从Excel文件中读取数据
try:
    df = pd.read_excel('dash_visu_export.xlsx', sheet_name='Sheet1')
    columns = df.columns
    if not all(column in columns for column in ['UTCI', 'GWP', 'LCC']):
        raise ValueError("Some columns are missing from the Excel sheet.")
except Exception as e:
    print(f"Error reading the Excel file: {e}")
    df = pd.DataFrame()

# 创建一个Dash应用程序
app = dash.Dash(__name__)

# 定义应用程序的布局
app.layout = html.Div([
    dcc.Graph(id='3d-mesh-plot', style={'width': '800px', 'height': '600px'})
])


@app.callback(
    Output('3d-mesh-plot', 'figure'),
    [Input('3d-mesh-plot', 'relayoutData')]
)
def update_3d_mesh_plot(relayoutData):
    if df.empty:
        return {}

    x = df['UTCI']
    y = df['GWP']
    z = df['LCC']

    # 创建一个 Mesh3d 对象
    mesh = go.Mesh3d(x=x, y=y, z=z, color='cyan', opacity=0.7, colorscale='Viridis')

    layout = go.Layout(scene=dict(aspectmode="cube"))

    # 添加坐标轴的标题
    layout.scene.xaxis.title = 'UTCI'
    layout.scene.yaxis.title = 'GWP'
    layout.scene.zaxis.title = 'LCC'

    fig = go.Figure(data=[mesh], layout=layout)

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
