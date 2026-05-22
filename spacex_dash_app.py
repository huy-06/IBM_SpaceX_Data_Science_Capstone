import os
import pandas as pd
import requests
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# 1. Tự động tải file dữ liệu spacex_launch_dash.csv từ IBM Cloud nếu chưa có trong thư mục
data_url = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv"
data_file = "spacex_launch_dash.csv"

if not os.path.exists(data_file):
    print("Đang tải tệp dữ liệu spacex_launch_dash.csv từ IBM Cloud...")
    response = requests.get(data_url)
    with open(data_file, 'wb') as f:
        f.write(response.content)
    print("Tải dữ liệu hoàn tất!")

# Đọc dữ liệu vào DataFrame
spacex_df = pd.read_csv(data_file)
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# 2. Khởi tạo ứng dụng Dash
app = dash.Dash(__name__)

# Thiết lập Layout giao diện cho Dashboard
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # TASK 1: Thêm Drop-down Menu để chọn Launch Site
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
        ],
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    html.Br(),

    # TASK 2: Biểu đồ tròn hiển thị kết quả phóng thành công
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    
    # TASK 3: Thanh kéo Range Slider để lọc khối lượng Payload
    dcc.RangeSlider(
        id='payload-slider',
        min=0, max=10000, step=1000,
        marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
        value=[min_payload, max_payload]
    ),
    html.Br(),

    # TASK 4: Biểu đồ phân tán thể hiện sự tương quan giữa Payload và kết quả phóng
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])


# --- CALLBACKS XỬ LÝ SỰ KIỆN TƯƠNG TÁC ---

# TASK 2 Callback: Cập nhật Pie Chart khi chọn Dropdown
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Hiển thị tổng số lần phóng thành công cho tất cả các bệ phóng
        fig = px.pie(
            spacex_df, 
            values='class', 
            names='Launch Site', 
            title='Total Success Launches By Site'
        )
    else:
        # Lọc dữ liệu cho bệ phóng được chọn cụ thể và vẽ tỷ lệ Success vs Fail
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        class_counts = filtered_df['class'].value_counts().reset_index()
        class_counts.columns = ['class', 'count']
        fig = px.pie(
            class_counts, 
            values='count', 
            names='class', 
            title=f'Total Success Launches for site {entered_site}'
        )
    return fig


# TASK 4 Callback: Cập nhật Scatter Chart khi di chuyển Slider hoặc chọn Dropdown
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    # Lọc dữ liệu theo khoảng khối lượng kéo trên Slider
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    filtered_df = spacex_df[mask]
    
    if entered_site == 'ALL':
        # Vẽ biểu đồ phân tán cho tất cả các bệ phóng
        fig = px.scatter(
            filtered_df, 
            x='Payload Mass (kg)', 
            y='class',
            color='Booster Version Category',
            title='Correlation between Payload and Success for all Sites'
        )
    else:
        # Lọc dữ liệu theo bệ phóng cụ thể
        site_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(
            site_df, 
            x='Payload Mass (kg)', 
            y='class',
            color='Booster Version Category',
            title=f'Correlation between Payload and Success for site {entered_site}'
        )
    return fig


# 3. Khởi chạy Server cục bộ
if __name__ == '__main__':
    app.run(port=8050)