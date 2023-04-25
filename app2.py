from dash import Dash, html, dash_table, dcc, callback, Output, Input
import json
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc

# currently, this app constitues a TREEMAP for customer segments with custom plot styling

# Set a plotly express template for aesthetically pleasing plots
px.defaults.template = "plotly_white"

# load clustered customer data
clustered_customer_data = pd.read_csv('Data/clustered_data.csv')

# instantiate a dash app with a dbc theme; include meta-tags for mobile viewing (add later)
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY],
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
        ]),
    dbc.Row([
        dbc.Col([
            html.Div(id='test-output')
        ])
    ])
    ])

# count number of clicks (to determine whether to expand or collapse)
click_counter = 0
@app.callback(
    Output('test-output', 'children'),
    Input('test', 'clickData')
)
def display_click_data(clickData):
    # count number of clicks (to determine whether to expand or collapse)
    global click_counter
    click_counter+=1
    # load click data dictionary
    if clickData:
        click_data = clickData["points"][0]
    else:
        return None
    # decide whether to expand or collapse (note that loading the page counts as a click)
    if click_counter % 2 == 0:
        # return click_data['label']
        return f'{round(click_data["value"] / 100000)/10} M'
    else:
        return None
    # below returns entire dictionary (for testing):
    # return json.dumps(clickData, indent=2)

if __name__ == '__main__':
    app.run_server(debug=True)