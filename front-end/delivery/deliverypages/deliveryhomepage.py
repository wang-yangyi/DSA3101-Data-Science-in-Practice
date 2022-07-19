import dash
from dash import dcc
from dash import callback
from dash import html
from dash import dash_table as dt
from dash.dependencies import Input, Output, State

import pandas as pd
import numpy as np
import plotly.express as px
import sqlalchemy
from datetime import date
import re
import requests

from datetime import datetime

from sqlalchemy import create_engine, inspect, select, text, and_, or_, func
from sqlalchemy import Table, MetaData

import pandas as pd

# Dash Bootstrap Components
import dash_bootstrap_components as dbc

#%% CSS
# the style arguments for the main content page.
CONTENT_STYLE = {
    'margin-left': '5%',
    'margin-right': '5%',
    'margin-bottom': '5%',
    'top': 0,
    'padding': '30px'
}

CARD_STYLE = {
    'margin': '2%',
    # 'padding': '30px',
    # 'padding-bottom': '15px',
    'text-align': 'center',
}

TEXT_STYLE = {
    'textAlign': 'center',
    'color': '#191970'
}

CARD_TEXT_STYLE = {
    'font-size': '35px',
    'textAlign': 'center',
    'height': '60px',
    'color': 'black'
}

CARD_TEXT_STYLE_RED = {
    'font-size': '35px',
    'textAlign': 'center',
    'height': '60px',
    'color': '#A30000'
}

CARD_FOOTER_STYLE = {
    'color': 'black',
    'background-color': '#FF9900'
}
#%% DATA

pwd = 'P5ZfmiRL'
engine = create_engine('mysql+pymysql://e0425282:' + pwd + '@13.251.201.156:3306/olist')

# Functions to query data into Pandas dfs
def as_pandas(results):
    columns = results.keys()
    rows = results.fetchall()
    df = pd.DataFrame(data=rows, columns=columns)
    return df

def sql_query(query):
    output = as_pandas(engine.execute(query))
    
    return output

# Dataframe of order statuses
order_status = sql_query('SELECT distinct(o.order_status) FROM olist.orders o')

orders_df = sql_query('SELECT * FROM olist.orders o')
orders_df['purchase_date'] = pd.to_datetime(orders_df['purchase_time']).dt.date

excl_delivered = orders_df[orders_df['order_status']!='delivered']

def card_num(orders_df, status):
    return orders_df[orders_df['order_status']==status]['order_id'].count()

# delayed_test = requests.get("http://127.0.0.1:5000/delayplotdata")
# delayed_dict = delayedplot.delay_plot_data()
# delayed_df = pd.DataFrame.from_dict(delayed_dict)

r = requests.get("http://backend:5001/delayplotdata")
data = r.text
delayed_df = pd.read_json(data)
#%% DASH APP

navbar = html.Div(
    html.Div(
        html.H3("Delivery Tracking System", style={'textAlign':'center', 'color': 'white', 'padding': '8px', 'margin-top': '0'})
    ),
    
    style = {'backgroundColor': '#131921'})

#drop down list: multi
dropdown = dcc.Dropdown(order_status, multi=True)

#data picker range
date_picker = dcc.DatePickerRange(
        id='date-picker-range',
        start_date=date(2016, 9, 4),
        end_date=date(2018, 10, 17),
        max_date_allowed=date(2018, 10, 17),
        min_date_allowed=date(2016, 9, 4),
        style={'margin-bottom':'10px'}
    )

search = dcc.Input(
    id='search-input', placeholder='Input Order ID Here', style={'margin-left': '15px', 'margin-bottom':'10px'}
    )
#%% 

delayed_line_chart = px.line(delayed_df, x='time_list', y='delay_list', labels={'time_list':"Date", 'delay_list':"Number of Delayed Deliveries"},
                             title='Number of Delayed Deliveries over time')

order_status_chart = px.pie(excl_delivered, names='order_status', title='Order Status (excluding "Delivered")', color_discrete_sequence=px.colors.sequential.RdBu) #order statuses excluding delivered

content_first_row = dbc.Row([
    dbc.Col(
        dbc.Card(
            [

                dbc.CardBody(
                    [
                        html.H4(id='card_title_1', children=[card_num(orders_df, 'delivered')], className='card-title',
                                style=CARD_TEXT_STYLE),
                    ]
                ),
                dbc.CardFooter('Orders Delivered', style=CARD_FOOTER_STYLE),
            ], color="success", outline=True
        ),
        md=3
    ),
    dbc.Col(
        dbc.Card(
            [

                dbc.CardBody(
                    [
                        html.H4(card_num(orders_df, 'shipped'), className='card-title', style=CARD_TEXT_STYLE)
                    ]
                ),
                dbc.CardFooter('Orders Shipped', style=CARD_FOOTER_STYLE),
            ], color="success", outline=True
        ),
        md=3
    ),
    dbc.Col(
        dbc.Card(
            [
                dbc.CardBody(
                    [
                        html.H4(card_num(orders_df, 'processing'), className='card-title', style=CARD_TEXT_STYLE)
                    ]
                ),
                dbc.CardFooter('Orders Processing', style=CARD_FOOTER_STYLE),
            ], color="success", outline=True

        ),
        md=3
    ),
    dbc.Col(
        dbc.Card(
            [

                dbc.CardBody(
                    [
                        html.H4(card_num(orders_df, 'canceled'), className='card-title', style=CARD_TEXT_STYLE_RED)
                    ]
                ),
                dbc.CardFooter('Orders Cancelled', style=CARD_FOOTER_STYLE),
            ], color="danger", outline=True

        ),
        md=3
    ),
], style=CARD_STYLE)

content_second_row = dbc.Row([
    dbc.Col(
        dbc.Card(
            [

                dbc.CardBody(
                    [
                        html.H4(id='card_title_2', children=[card_num(orders_df, 'created')], className='card-title',
                                style=CARD_TEXT_STYLE)
                    ]
                ),
                dbc.CardFooter('Orders Created', style=CARD_FOOTER_STYLE),
            ], color="success", outline=True
        ),
        md=3
    ),
    dbc.Col(
        dbc.Card(
            [
                dbc.CardBody(
                    [
                        html.H4(card_num(orders_df, 'approved'), className='card-title', style=CARD_TEXT_STYLE)
                    ]
                ),
                dbc.CardFooter('Orders Approved', style=CARD_FOOTER_STYLE),
            ], color="success", outline=True
        ),
        md=3
    ),  
    dbc.Col(
        dbc.Card(
            [
                dbc.CardBody(
                    [
                        html.H4(card_num(orders_df, 'invoiced'), className='card-title', style=CARD_TEXT_STYLE)
                    ]
                ),
                dbc.CardFooter('Orders Invoiced', style=CARD_FOOTER_STYLE),
            ], color="success", outline=True

        ),
        md=3
    ),
    dbc.Col(
        dbc.Card(
            [
                dbc.CardBody(
                    [
                        html.H4(card_num(orders_df, 'unavailable'), className='card-title', style=CARD_TEXT_STYLE_RED)
                    ]
                ),
                dbc.CardFooter('Orders Unavailable', style=CARD_FOOTER_STYLE),
            ], color="danger", outline=True
        ),
        md=3
    )
], style=CARD_STYLE)

content_third_row = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(id='graph_1', figure=order_status_chart, style={'margin':'20px'}), md=4
        ),
        dbc.Col(
            dcc.Graph(id='graph_2', figure=delayed_line_chart), md=8
        )
    ]
)

content_fourth_row = html.Div(
    children=[
        date_picker,
        search,
        dcc.Dropdown(
            id="filter_dropdown",
            options=[{"label": st, "value": st} for st in order_status['order_status']],
            placeholder="Filter by order status",
            multi=True,
            value=np.unique(orders_df.order_status.values),
            style={'margin-bottom':'10px'}
        ),
        dt.DataTable(
            id="table-container",
            columns=[{"name": i, "id": i, "presentation": "markdown"} for i in orders_df.loc[:, ['order_id', 'customer_id', 'order_status', 'estimated_delivery', 'purchase_date']]],
            data=orders_df.to_dict("records"),
            is_focused=True,
            style_data_conditional=[
                {'if': {'column_id': 'Symbol'}, 'backgroundColor': 'green', 'text_align':'center','color': 'white'},
                {'if': {'column_id': '% Change'}, 'backgroundColor': 'yellow', 'color': 'red', 'font-weight': 'bold'},
                                   ],
        ),
        html.Div(id="output"),
    ],
    style=CONTENT_STYLE
)

content = html.Div(
    [
        navbar,
        content_first_row,
        content_second_row,
        content_third_row,
        # date_picker,
        content_fourth_row
    ],
    # style=CONTENT_STYLE
)

layout = html.Div([content])

@callback(
    Output("table-container", "data"), 
    Input("filter_dropdown", "value"),
    Input("date-picker-range", "start_date"),
    Input("date-picker-range", "end_date"),
    Input("search-input", "value")
)

def display_table(status, start_date, end_date, search):
    dff = orders_df[orders_df.order_status.isin(status)]
    
    # if start_date and end_date:
    mask = (dff["purchase_date"] >= datetime.strptime(start_date, '%Y-%m-%d').date()) & (
        dff["purchase_date"] <= datetime.strptime(end_date, '%Y-%m-%d').date())
    dff = dff.loc[mask]
    
    if search:
        mask2 = (dff["order_id"] == search)
        dff = dff.loc[mask2]
    # dff = orders_df[orders_df.order_status.isin(status)]
    return dff.to_dict("records")


@callback(
    Output("output", "children"),
    Input("table-container", "active_cell"),
    State("table-container", "derived_viewport_data"),
)

def cell_clicked(active_cell, data):
    
    data = orders_df.to_dict("records")
    
    if active_cell:
        row = active_cell["row"]
        col = active_cell["column_id"]

        if col == "order_id":  # or whatever column you want
            selected = data[row][col]
            
            return dcc.Location(pathname="/order/{}".format(selected), id = "somethingrandom")
        else:
            return dash.no_update

# def cell_clicked(active_cell, data, start_date, end_date):
#     data = orders_df.to_dict("records")
#     if active_cell:
#         row = active_cell["row"]
#         col = active_cell["column_id"]

#         if col == "order_id":  # or whatever column you want
#             selected = data[row][col]
            
#             return dcc.Location(pathname="/order/{}".format(selected), id = "somethingrandom")
#         # else:
#         #     return dash.no_update
        
#     if start_date and end_date:
#         mask = (date_string_to_date(orders_df["purchase_date"]) >= date_string_to_date(start_date)) & (
#             date_string_to_date(orders_df["purchase_date"]) <= date_string_to_date(end_date)
#         )
#         data = orders_df.loc[mask].to_dict("records")
#     return data
    
# def update_output(active_cell, data, start_date, end_date):
#     data = orders_df.to_dict("records")
#     if start_date and end_date:
#         mask = (date_string_to_date(orders_df["purchase_date"]) >= date_string_to_date(start_date)) & (
#             date_string_to_date(orders_df["purchase_date"]) <= date_string_to_date(end_date)
#         )
#         data = orders_df.loc[mask].to_dict("records")
#     return data

# if __name__ == '__main__':
#     app.run_server(debug=True)