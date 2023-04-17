from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc

# currently, this app constitues a TREEMAP for customer segments with custom plot styling

# Set a plotly express template for aesthetically pleasing plots
px.defaults.template = "plotly_white"

# load clustered customer data
clustered_customer_data = pd.read_csv('Data/clustered_data.csv')

# instantiate a dash app with a dbc theme; include meta-tags for mobile viewing (add later)
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
           meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}])

# customize treemap figure using figure.update_traces method
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

# configure the app's layout using a dbc container with rows and columns
# add labelClassName styling using dbc later
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='test', figure=PAC_fig)
            ])
        ])
    ])

if __name__ == '__main__':
    app.run_server(debug=True)