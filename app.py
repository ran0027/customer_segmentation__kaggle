from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from zipfile import ZipFile

# Set mapbox public access token
px.set_mapbox_access_token(open(".mapbox_token").read())

# Incorporate data
with ZipFile('Data/customer_shopping.zip') as zipArchive:
    with zipArchive.open('customer_shopping_data.csv') as f:
        df = pd.read_csv(f)

raw_df = df.copy()
df['invoice_date'] = pd.to_datetime(df.invoice_date, format='%d/%m/%Y')
monthly_by_mall = df.groupby('shopping_mall').resample('M', on='invoice_date').sum()['price'].reset_index()

df2 = pd.read_csv('Data/clustered_data.csv')

df3 = pd.DataFrame({'latitude': [40.993815, 40.93798668888122, 41.06691465715547, 41.076171181311075,
                                 41.062445142091775, 41.07806746284409, 41.11045056431461,
                                 41.047472970904614, 41.00338683267939, 41.063042285586896],
                    'longitude': [29.122310, 29.323871662803867, 29.017085878734076, 29.013476280734576,
                                  28.807044938256283, 29.009985679240053, 29.032813373203187,
                                  28.896730484333407, 29.071487170670302, 28.992591021697415],
                    'shopping_mall': ['Metropol AVM', 'Viaport Outlet', 'Zorlu Center', 'Metrocity',
                           'Mall of Istanbul', 'Kanyon', 'Istinye Park', 'Forum Istanbul',
                           'Emaar Square Mall', 'Cevahir AVM']})

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
           meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='mall-line-graph', figure={})
        ], width={'size': 4, 'offset': 0}),
        dbc.Col([
            dcc.Checklist(id='mall-checklist', value=['Cevahir AVM'],
                          options=[{'label': x, 'value': x} for x in sorted(df['shopping_mall'].unique())],
                          labelClassName='')
        ], width={'size': 1, 'offset': 0}),
        dbc.Col([
            dcc.Graph(id='spend-per-cluster', figure=px.histogram(df2, x='cluster', y='price', histfunc='sum',
                                                                  title='Total Spend per Cluster'))
        ], width={'size': 3, 'offset': 1}),
        dbc.Col([
            dcc.Graph(id='customers-per-cluster', figure=px.histogram(df2, x='cluster', y='quantity',
                                                                      histfunc='count',
                                                                      title='Number of Customers per Cluster'))
        ], width={'size': 3, 'offset': 0})
    ], justify='center', align='center', className='g-0'),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='map-of-malls', figure=px.scatter_mapbox(data_frame=df3, lat='latitude', lon='longitude',
                                                       hover_name='shopping_mall'))
        ], width={'size': 5, 'offset': 0}),
        dbc.Col([
            html.Div(
                children=f"Average monthly income:\n{raw_df.groupby('shopping_mall').sum()['price'].mean()}", className=''
            ),
            html.Div(
                children=f'Top-selling category:\n{raw_df.category.value_counts().index[0]}', className=''
            )
        ], width={'size': 1, 'offset': 0}),
        dbc.Col([
            dcc.RadioItems(id='select-category-for-pie', value='Tech and Shoes',
                            options=['Tech and Shoes', 'Women', 'Men', 'Parents'])
        ], width={'size': 1, 'offset': 1}),
        dbc.Col([
            dcc.Graph(id='categories-by-cluster', figure={})
        ], width={'size': 3, 'offset': 0})
    ], justify='between', align='center', className='g-0')
], fluid=True)

@callback(
    Output(component_id='mall-line-graph', component_property='figure'),
    Input(component_id='mall-checklist', component_property='value')
)
def update_graph(chosen_malls):
    fig = px.line(monthly_by_mall.loc[monthly_by_mall.shopping_mall.isin(chosen_malls)],
                  x="invoice_date", y="price", color="shopping_mall", title='Monthly Income')
    return fig

@callback(
    Output(component_id='categories-by-cluster', component_property='figure'),
    Input(component_id='select-category-for-pie', component_property='value')
)
def update_pie(chosen_cluster):
    fig = px.pie(df2.loc[df2.cluster == chosen_cluster], names='category', values='price')
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)