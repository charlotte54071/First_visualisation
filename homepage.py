# 导入所需库
import dash
from dash import html
from dash.dependencies import Input, Output, State

# 初始化 Dash 应用
app = dash.Dash(__name__)

# 应用布局
app.layout = html.Div([
    # 主页上的图片链接
    html.Div([
        html.Img(src='/assets/house.png', id='img1', n_clicks=0),
        html.Img(src='/assets/city.png', id='img2', n_clicks=0),
        html.Img(src='/assets/room.png', id='img3', n_clicks=0)
    ]),

    # 用于显示不同页面内容的 Div
    html.Div(id='page-content')
])

# 回调函数来更新页面内容
@app.callback(
    Output('page-content', 'children'),
    [Input('img1', 'n_clicks'), Input('img2', 'n_clicks'), Input('img3', 'n_clicks')],
)
def display_page(n1, n2, n3):
    # 根据点击的图片更新页面
    ctx = dash.callback_context
    if not ctx.triggered:
        return "Welcome to the homepage!"
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == 'img1':
            return html.Div([
                html.H3("Page 1"),
                html.P("This is the content of the first page.")
            ])
        elif button_id == 'img2':
            return html.Div([
                html.H3("Page 2"),
                html.P("This is the content of the second page.")
            ])
        elif button_id == 'img3':
            return html.Div([
                html.H3("Page 3"),
                html.P("This is the content of the third page.")
            ])

# 运行应用
if __name__ == '__main__':
    app.run_server(debug=True)
