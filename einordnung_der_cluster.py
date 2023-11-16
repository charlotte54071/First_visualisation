from dash import Dash, dcc, html
import pandas as pd
import plotly.graph_objs as go

# 尝试加载 Excel 数据
try:
    df = pd.read_excel('dash_visu_export.xlsx', sheet_name='Sheet1')
    columns = df.columns
    if not all(column in columns for column in ['UTCI', 'GWP', 'LCC']):
        raise ValueError("Some columns are missing from the Excel sheet.")
except Exception as e:
    print(f"Error reading the Excel file: {e}")
    df = pd.DataFrame()

# 数据处理
indicators = ['UTCI', 'GWP', 'LCC']
avg_df = df.groupby('cluster').mean()

def normalize(column):
    max_value = column.max()
    min_value = column.min()
    return (column - min_value) / (max_value - min_value)

normalized_avg_df = avg_df[indicators].apply(normalize)

# 创建 Dash 应用
app = Dash(__name__)

# 定义页面布局
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div([
        html.A(html.Img(src='/assets/house.png', id='img1'), href='/page-1'),
        html.A(html.Img(src='/assets/city.png', id='img2'), href='/page-2'),
        html.A(html.Img(src='/assets/room.png', id='img3'), href='/page-3'),
    ]),
    html.Div(id='page-content')
])

# 根据 URL 显示不同的图表页面
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/page-1':
        return generate_chart('UTCI')
    elif pathname == '/page-2':
        return generate_chart('GWP')
    elif pathname == '/page-3':
        return generate_chart('LCC')
    else:
        return "Welcome to the homepage!"

# 生成图表的函数
def generate_chart(indicator):
    return dcc.Graph(
        id=f'{indicator}-chart',
        figure={
            'data': [
                {'x': normalized_avg_df.index, 'y': normalized_avg_df[indicator], 'type': 'bar', 'name': indicator}
            ],
            'layout': {
                'title': f'Cluster Analysis for {indicator}',
                'xaxis': {'title': 'Cluster Number'},
                'yaxis': {'title': indicator}
            }
        }
    )

if __name__ == '__main__':
    app.run_server(debug=True)
