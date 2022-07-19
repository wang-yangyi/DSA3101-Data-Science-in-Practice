#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from dash.dependencies import Input, Output
import re
from deliverypages import order, deliveryhomepage
import dash_bootstrap_components as dbc

FONT_AWESOME = "https://use.fontawesome.com/releases/v5.10.2/css/all.css"

# Create Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=([dbc.themes.COSMO, FONT_AWESOME]))

app.layout = html.Div([
    dcc.Location(id = "url", refresh=False),
    html.Div(id = "page-content")
])

@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def display_page(pathname):
    if '/order' in pathname:
        return order.layout
    else:
        return deliveryhomepage.layout


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True)