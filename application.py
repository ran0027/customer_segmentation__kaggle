from flask import Flask
from dash import Dash, html, dash_table, dcc, callback, Output, Input, State
import boto3
import os
import json
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc

### ACCESS DATA

## Locally
# clustered_customer_data = pd.read_csv('Data/clustered_data.csv')

## From the cloud
# access S3 keys from config variables set on Heroku
import s3fs

KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
BUCKET = 'customer-segmentation-kaggle'
fp = 's3://customer-segmentation-kaggle/clustered_data.csv'


fs = s3fs.S3FileSystem(anon=False, key=KEY_ID, secret=ACCESS_KEY)

with fs.open(fp) as f:
   clustered_customer_data = pd.read_csv(f)

# only works if using s3 client / resource, not s3fs via pandas
# AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
# AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']

# same here:
# session = boto3.Session(
#     aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
#     aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY']
# )

# load clustered customer data from S3 bucket
# clustered_customer_data = pd.read_csv('s3://customer-segmentation-kaggle/clustered_data.csv')

### APP
## Flask app
flask_app = Flask(__name__)

## Dash app
# instantiate a dash app with a dbc theme; include meta-tags for mobile viewing (add later)
app = Dash(__name__,
           server=flask_app,
           external_stylesheets=[dbc.themes.FLATLY],
           prevent_initial_callbacks="initial_duplicate",
           meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}])

### FIGURE (treemap)
# instantiate and customize treemap figure for displaying customer segmentation
PAC_fig = px.treemap(clustered_customer_data,
                     path = ['cluster'],
                     values='price'
                     )
PAC_fig.update_traces(marker=dict(cornerradius=5),
                      textposition='middle center',
                      hovertemplate = 'Total Gross:<br>&nbsp;&nbsp;&nbsp;%{value:$,.3s}', # d3.format formatting
                      hoverlabel_bordercolor='slategray',
                      hoverlabel_font = dict(color='white', family='Balto'),
                      insidetextfont=dict(color='white', family='Balto', size=30),
                      outsidetextfont=dict(color='slategray', family='Balto', size=26))
PAC_fig.update_layout(margin=dict(l=20, r=20, t=0, b=20))

### APP LAYOUT
# specify app layout with TWO ROWS
# (one for treemap, showing relationship b/w clusters,
#  & one for tabs // to select an individual cluster and display more info)
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H3('Customer Segments', className='text-center mt-5 mb-0'),
            html.P('Customer segments were obtained via k-means clustering.',
                className='mt-2 ms-4 mb-0 text-muted'),
            html.P(id='click-data'),
            dcc.Graph(id='treemap', figure=PAC_fig)
        ])
    ], justify='center'),
    dbc.Row([
        dbc.Tabs(
            [dbc.Tab(label='Tech and Shoes', tab_id='tab0'),
             dbc.Tab(label='Women', tab_id='tab1'),
             dbc.Tab(label='Men', tab_id='tab2'),
             dbc.Tab(label='Parents', tab_id='tab3')],
             id='tabs'
        ),
        # this store lets us access the tab label via the tab id
        dcc.Store(id='tab-labels', data=json.dumps(
            {'tab0': 'Tech and Shoes',
             'tab1': 'Women',
             'tab2': 'Men',
             'tab3': 'Parents'}
        )),
        html.Div(id='tab-content')
    ])
])

### CALLBACKS (tabs)
# update tab content based on selected tab
@app.callback(
        Output('tab-content', 'children'),
        Input('tabs', 'active_tab'),
        State('tab-labels', 'data')
)
def update_tab_content(active_tab, tab_labels):
    # get cluster name for active_tab
    cluster = json.loads(tab_labels)[active_tab]
    # get data for cluster
    df = clustered_customer_data.loc[clustered_customer_data.cluster == cluster]
    df_aggregated = df.groupby(['category'], as_index=False).sum()

    # instantiate and customize figure for spending breakdown

    # # OLD: pie chart
    # fig = px.pie(df_aggregated, values='price', names='category', title='Spending Breakdown for Cluster')

    # bar graph
    fig = px.bar(df_aggregated, x='category', y='price', text_auto='.2s')
    # not in use yet: hover df to get cluster average "spend per item" for each category
    # hover_df = df.groupby(['category'], as_index=False).mean()['price_per_item']
    fig.update_layout(title='Spending Breakdown for Segment',
                      title_x=0.5,
                      yaxis=dict(title='Total Gross to Date (in $)'),
                      xaxis=dict(title='',
                                 categoryorder='total descending'))
    fig.update_traces(hovertemplate=None, hoverinfo='skip')

    # build row of items to display in "tab-content" div
    row = dbc.Row([
            dbc.Col([
                html.Div(children=[
                    # cluster name
                    html.H1(cluster),
                    # total gross to date
                    html.H2(f'Total Gross to Date: ${round(df["price"].sum() / 100000)/10} M')])
            ]),
            dbc.Col([
                # pie chart with spending by category
                dcc.Graph(figure=fig)
            ])
    ])
    return row

# ADD: treemap click triggers active_tab selection

# @app.callback(
#     Output('click-data', 'children'),
#     Input('treemap', 'clickData'))
# def display_click_data(clickData):
#     return json.dumps(clickData)

### RUN LOCALLY
# if __name__ == '__main__':
#     app.run_server(debug=True, port=8050, host='127.0.0.1')

### DEPLOY (Heroku)
if __name__ == '__main__':
    app.run_server(debug=True)