#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import dash
from dash import dcc
from dash import html
from dash import callback
from dash import dash_table as dt
from dash.dependencies import Input, Output

import pandas as pd
import numpy as np
import plotly.express as px
import sqlalchemy
from datetime import date
import requests
import re

from sqlalchemy import create_engine, inspect, select, text, and_, or_, func
from sqlalchemy import Table, MetaData

import pandas as pd

# Dash Bootstrap Components
import dash_bootstrap_components as dbc

FONT_AWESOME = "https://use.fontawesome.com/releases/v5.10.2/css/all.css"

#%% CSS
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

card_icon = {
    "color": "white",
    "textAlign": "center",
    "fontSize": 30,
    "margin": "auto",
}

#%% DATA

# Connect to Database
# with open('/Users/admin/Desktop/DSA3101/DSA3101 Delivery/pages/dbase_pwd.txt', 'r') as f:
#     pwd = f.readlines()[1].split()[1]

pwd = 'P5ZfmiRL'
engine = create_engine('mysql+pymysql://e0425282:' + pwd + '@13.251.201.156:3306/olist')

# with engine.connect() as con:
#     rs = con.execute("select * from orders limit 20")
#     data = rs.fetchmany(size=10) 

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
excl_delivered = orders_df[orders_df['order_status']!='delivered']

def card_num(orders_df, status):
    return orders_df[orders_df['order_status']==status]['order_id'].count()

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
        start_date=date(2022, 1, 1),
        end_date_placeholder_text='Select a date!'
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

list_grp = html.Div(id='order-table')

content_fourth_row = html.Div(dcc.Link(
    html.Button('Back', id='btn-nclicks-1', n_clicks=0, style=CARD_STYLE), href='http://localhost:8050', refresh=True)
    )

content_fifth_row = html.Div(
    html.Div( style={'background-color':'#eaeded', 'margin':'25px', 'padding-bottom': '25px'},
    children=[
        content_fourth_row,
        list_grp
    ]
))

content = html.Div(
    [
        navbar,
        content_first_row,
        content_second_row,
        content_third_row,
        # content_fourth_row,
        content_fifth_row
    ],
    # style=CONTENT_STYLE
)

layout = html.Div([
    dcc.Location(id='order-url', refresh=False),
    html.Div([content])
    ])

# @callback(
#     Output('container-button-timestamp', 'children'),
#     Input('btn-nclicks-1', 'n_clicks'),
#     Input("order-url", "pathname")
# )
# def displayClick(btn1):
#     changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
#     if 'btn-nclicks-1' in changed_id:    
#         return dcc.Location(pathname="", id = "somethingrandom")

def get_info(attr, order_id):
    res = orders_df[orders_df['order_id']==order_id][attr]
    return res

@callback(
    Output("order-table", "children"), 
    Input("order-url", "pathname")
)

def get_order_id(pathname):
    if pathname != None:
        order_id = pathname.split('/')[-1]
        return html.Div([
            dbc.Row([
            dbc.Col(
                dbc.CardGroup(
                [
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5("Order ID", className="card-title"),
                                html.P(order_id, className="card-text",),
                            ]
                        )
                    ),
                    dbc.Card(
                        html.Div(className="fas fa-envelope", style=card_icon),
                        style={"maxWidth": 75, 'background-color': '#FF9900'},
                    ),
                    
                ],
                className="mt-4 shadow",
            ),
                md=3
            ),
            
            dbc.Col(
                dbc.CardGroup(
                [
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5("Customer ID", className="card-title"),
                                html.P(get_info('customer_id', order_id), className="card-text",),
                            ]
                        )
                    ),
                    dbc.Card(
                        html.Div(className="fas fa-user", style=card_icon),
                        style={"maxWidth": 75, 'background-color': '#FF9900'},
                    ),
                   
                ],
                className="mt-4 shadow",
            ),
                md=3
            ),
            dbc.Col(
                dbc.CardGroup(
                [
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5("Order Status", className="card-title"),
                                html.P(get_info('order_status', order_id), className="card-text",),
                            ]
                        )
                    ),
                    dbc.Card(
                        html.Div(className="fa fa-info", style=card_icon),
                        style={"maxWidth": 75, 'background-color': '#FF9900'},
                    ),
                    
                ],
                className="mt-4 shadow",
            ),
                md=3
            ),
            dbc.Col(
                dbc.CardGroup(
                [
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5("Estimated Delivery", className="card-title"),
                                html.P(get_info('estimated_delivery', order_id), className="card-text",),
                            ]
                        )
                    ),
                    dbc.Card(
                        html.Div(className="fas fa-clock", style=card_icon),
                        style={"maxWidth": 75, 'background-color': '#FF9900'},
                    ),
                    
                ],
                className="mt-4 shadow",
            ),
                md=3
            )
        ], style=CARD_STYLE),
            dbc.Row([
            dbc.Col(
                dbc.CardGroup(
                [
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5("Purchase Time", className="card-title"),
                                html.P(get_info('purchase_time', order_id), className="card-text",),
                            ]
                        )
                    ),
                    dbc.Card(
                        html.Div(className="fas fa-money-bill-alt", style=card_icon),
                        style={"maxWidth": 75, 'background-color': '#FF9900'},
                    ),
                    
                ],
                className="mt-4 shadow",
            ),
                md=3
            ),
            
            dbc.Col(
                dbc.CardGroup(
                [
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5("Approval Time", className="card-title"),
                                html.P(get_info('approval_time', order_id), className="card-text",),
                            ]
                        )
                    ),
                    dbc.Card(
                        html.Div(className="fas fa-thumbs-up", style=card_icon),
                        style={"maxWidth": 75, 'background-color': '#FF9900'},
                    ),
                   
                ],
                className="mt-4 shadow",
            ),
                md=3
            ),
            dbc.Col(
                dbc.CardGroup(
                [
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5("Delivered to Carrier", className="card-title"),
                                html.P(get_info('delivered_carrier', order_id), className="card-text",),
                            ]
                        )
                    ),
                    dbc.Card(
                        html.Div(className="fas fa-boxes", style=card_icon),
                        style={"maxWidth": 75, 'background-color': '#FF9900'},
                    ),
                    
                ],
                className="mt-4 shadow"
            ),
                md=3
            ),
            dbc.Col(
                dbc.CardGroup(
                [
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5("Delivered to Customer", className="card-title"),
                                html.P(get_info('delivered_customer', order_id), className="card-text",),
                            ]
                        )
                    ),
                    dbc.Card(
                        html.Div(className="fas fa-shipping-fast", style=card_icon),
                        style={"maxWidth": 75, 'background-color': '#FF9900'},
                    ),
                    
                ],
                className="mt-4 shadow",
            ),
                md=3
            )
        ], style=CARD_STYLE)])

