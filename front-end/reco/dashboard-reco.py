import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from dash.dependencies import Input, Output
import re
from recopages import category, homepage, product


# Create Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div([
    dcc.Location(id = "url", refresh=False),
    html.Div(id = "page-content")
])

@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def display_page(pathname):
    if '/product' in pathname:
        return product.layout
    elif '/category' in pathname:
        return category.layout
    else:
        return homepage.layout


if __name__ == '__main__':
    app.run_server(host='0.0.0.0',debug=True, port=8051)