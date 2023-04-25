from dash import Dash, html, dash_table, dcc, callback, Output, Input, State
import json
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc

# Set a plotly express template for aesthetically pleasing plots
px.defaults.template = "plotly_white"

# load clustered customer data
clustered_customer_data = pd.read_csv('Data/clustered_data.csv')

# instantiate a dash app with a dbc theme; include meta-tags for mobile viewing (add later)
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY],
           prevent_initial_callbacks="initial_duplicate",
           meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}])

# instantiate and customize treemap figure for displaying customer segmentation
PAC_fig = px.treemap(clustered_customer_data,
                     path=[px.Constant("Hover for Total Gross to Date"), 'cluster'],
                     values='price'
                     )
PAC_fig.update_traces(marker=dict(cornerradius=5),
                      textposition='middle center',
                      hovertemplate = 'Total Gross:<br>&nbsp;&nbsp;&nbsp;%{value:$,.3s}', # d3.format formatting
                      hoverlabel_bordercolor='slategray',
                      hoverlabel_font = dict(color='white', family='Balto'),
                      insidetextfont=dict(color='white', family='Balto', size=16),
                      outsidetextfont=dict(color='slategray', family='Balto', size=26))

# specify app layout with TWO ROWS
# (one for treemap, showing relationship b/w clusters,
#  & one for tabs // to select an individual cluster and display more info)
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H3('Customer Segments'),
            dcc.Graph(id='treemap', figure=PAC_fig)
        ])
    ]),
    dbc.Row([
        dbc.Tabs(
            [dbc.Tab(label='Tech and Shoes', tab_id='tab0'),
             dbc.Tab(label='Women', tab_id='tab1'),
             dbc.Tab(label='Men', tab_id='tab2'),
             dbc.Tab(label='Parents', tab_id='tab3')],
             id='tabs',
             active_tab='Tech and Shoes'
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

# update tab content based on selected tab
@app.callback(
        Output('tab-content', 'children'),
        Input('tabs', 'active_tab'),
        State('tab-labels', 'data'),
        prevent_initial_call=True # don't run when page loads
)
def update_tab_content(active_tab, tab_labels):
    # get cluster name for active_tab
    cluster = json.loads(tab_labels)[active_tab]
    # get data for cluster
    df = clustered_customer_data.loc[clustered_customer_data.cluster == cluster]
    # build pie chart of spending by category for that cluster
    fig = px.pie(df, values='price', names='category', title='Spending Breakdown for Cluster')
    # build row of items to display in "tab-content" div
    row = dbc.Row([
            dbc.Col([
                html.Div(children=[
                    # cluster name
                    html.H1(cluster),
                    # total gross to date
                    html.H2(f'Total Gross to Date: {round(df["price"].sum() / 100000)/10} M')])
            ]),
            dbc.Col([
                # pie chart with spending by category
                dcc.Graph(figure=fig)
            ])
    ])
    return row

if __name__ == '__main__':
    app.run_server(debug=True, port=8050, host='127.0.0.1')