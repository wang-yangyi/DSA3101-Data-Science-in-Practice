import dash
from dash import callback
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash import callback_context
import pandas as pd
import plotly.express as px
from sqlalchemy import all_, create_engine
from dash.dependencies import Input, Output, State
import re
import requests
import random
import math


# Connecting to mysql
passwd = 'Y5cKZQEI'
engine = create_engine('mysql+pymysql://e0424903:' + passwd + '@13.251.201.156:3306/olist')


# convert results to dataframe
def as_pandas(results):
    columns = results.keys()
    rows = results.fetchall()
    df = pd.DataFrame(data=rows, columns=columns)
    return df


## ALL CATEGORIES ##
# Get list of category sorted alphabetically
def get_cat_dict(engine):   

    # English
    statement = """SELECT DISTINCT(p.english) \
                            FROM olist.prod_cat_name p"""
    cat_list = as_pandas(engine.execute(statement))
    cat_list_cleaned = cat_list['english'].map(lambda x: re.sub("(\r)","",x))
    cat_list_cleaned = cat_list_cleaned.map(lambda x: re.sub("_"," ",x).title())

    cat_ori_tmp = cat_list.values.tolist()
    cat_ori = []
    for cat in cat_ori_tmp:
        tmp = cat[0]
        cat_ori.append(tmp)
    cat_english = [cat for cat in cat_list_cleaned]
    
    category_dict = {}
    for i in range(0, len(cat_ori)):
        eng_cleaned = cat_english[i]
        eng_original = cat_ori[i]
        category_dict[eng_cleaned] = eng_original

    return category_dict
category_dict = get_cat_dict(engine)
    
def get_cat_list(engine):
    statement = """SELECT DISTINCT(p.english) \
                            FROM olist.prod_cat_name p"""
    cat_list = as_pandas(engine.execute(statement))
    cat_list_cleaned = cat_list['english'].map(lambda x: re.sub("(\r)","",x))
    cat_list_cleaned = cat_list_cleaned.map(lambda x: re.sub("_"," ",x).title())
    cat_options = [cat for cat in cat_list_cleaned]
    cat_options.sort()
    return cat_options
categories = get_cat_list(engine)


## GET PRODUCT FULL INFO ##
def get_full_product_info(engine):
    statement = """SELECT p.product_id, p.category_name, c.english \
                    FROM olist.products p, olist.prod_cat_name c \
                    WHERE p.category_name = c.portugese
                """
    list = as_pandas(engine.execute(statement))
    list['english'] = list['english'].map(lambda x: re.sub("(\r)","",x))
    list['english'] = list['english'].map(lambda x: re.sub("_"," ",x).title())

    list['url'] = list['english'].map(lambda x: re.sub(" ","%20",x))

    list['english'] = list['english'].map(lambda x: re.sub(" ","",x))
    return list


## GENERATE PRODUCT CARD ##
def generate_product_card(row):
    pdt_id_short = row['product id'][-5:]
    pdt_id_full = row['product id']
    price = row['average price']
    sale = row['total sale']
    rating = '{:.1f}'.format(row['average score'])
    captial_eng_short = row['english'][:24]
    captial_eng_full = row['english']
    lower_eng = row['english'].lower()

    if 'seller info' in row:
        seller = row['seller info']
    else:
        seller = row['seller id']

    url_category = row['url']
    url_pdt_name = captial_eng_full + '-' + pdt_id_short
    url_pdt_id = pdt_id_full
    
    return html.A(
            dbc.Card([
                dbc.CardImg(src = "/assets/{}.jpeg".format(lower_eng), top = True),
                dbc.CardBody([
                    html.P("{}-{}".format(captial_eng_short,pdt_id_short)),
                    html.P("${:.2f}".format(price)),
                    html.P(""),
                    html.Div(
                        children = [
                            html.P("{} sold".format(sale), style = {"width":"50%"}),
                            html.P("{} / 5.0".format(rating), style = {"width":"50%", "text-align":"right"})
                        ],
                        style = {"display": "flex", "text-align": "justify"}
                    ),
                ])
            ], 
            className = "product"), 
        href="/{}/product/{}_{}by{}".format(url_category, url_pdt_name, url_pdt_id, seller))


## PAGE SIZE ##
pg_size = 30


## LAYOUT ##
layout = html.Div([

    dcc.Location(id='category-url', refresh=False),
    
    html.Div([
        html.Div([
            html.A(html.H3("Recommendation System"), href="/homepage", className='navlink')],
            className = 'nav'
        ),
        html.Div([
            dcc.Dropdown(id = "category-dropdown",
                        options = categories,
                        placeholder = "Search Category",
                        searchable = True),
            html.Div(id = "category-page-search-bar")], 
            className = 'nav'
        )
    ], 
    className = 'container-navbar'
    ),

    html.Div(id = 'category-page-breadcrumb'),
    
    html.Div(id = 'category-name', style = {"margin": "-10px 0px 20px 0px"}),

    html.Div(
        id = "category-page-all-products",
        children = [
            html.Div(
                children = [
                    html.H4(
                        "ALL PRODUCTS", 
                        style = {"font-weight":"bold", "margin": "0px 10px", "color": "#FA8128"}
                    ),

                    html.Div(
                        children = [
                            dbc.Button(
                                "Overall", 
                                id = "all-products-rank-score-button",
                                n_clicks = 0,
                                style = {"margin": "0px 10px"}
                            ),

                            dbc.Button(
                                "Price", 
                                id = "all-products-price-button",
                                n_clicks = 0,
                                style = {"margin": "0px 10px"}
                            ),
                            
                            dbc.Button(
                                "Top Sales", 
                                id = "all-products-top-sales-button",
                                n_clicks = 0,
                                style = {"margin": "0px 10px"}
                            ),
                            html.Div(
                                id = 'clicked-button', 
                                children = 'overall:0 price:0 sales:0 last:nan', 
                                style= {'display': 'none'})
                        ],
                        className = 'container-product-filter'
                    )
                ],
                style = {"margin": "20px 10px 0px 10px", "padding": "20px 0px 20px 0px"},
                className = 'container-heading-n-filter'
            ),

            html.Div(id = 'all-products-card'),
            # html.Div(id = 'all-products-pagination'),
            dbc.Pagination(
                id = 'all-products-pagination', 
                # min_value = 1,
                active_page = 1,
                max_value = 10, 
                first_last = True, 
                previous_next = True, 
                # fully_expanded = False,
                className = 'pagination',
                style = {"margin": "40px 0px"}
            ) 
        ],
        className = "container-general"
    ),

    html.Div(
        id = "category-page-other-products",
        children = [
            html.Div(
                style = {"grid-row":1, "margin": "0px 10px"},
                children = [
                    html.Div(
                        [html.H4(
                            "YOU MAY ALSO LIKE", 
                            style = {"font-weight":"bold", "color": "#FA8128"}
                        )],
                        style = {"margin": "20px 10px 0px 10px", "padding": "10px 0px 0px 0px"}
                    )
                ]
            ),
            
            html.Div(id="ymal-products-card"),
        ],

        className = "container-general"
    )
], 
style = {"background-color": "#eaeded", "padding": "0px 0px 30px 0px"}
)


## CATEGORY DROPDOWN SEARCH BAR ##
@callback(
    Output("category-page-search-bar", "children"),
    Input("category-dropdown", "value")
)
def route_to_page(value):
    if value != None:
        return dcc.Location(pathname="/category/{}".format(value), id = "somethingrandom")


## CATEGORY PAGE TITLE ##
@callback(
    Output("category-name", "children"),
    Input("category-url", "pathname")
)
def extract_category(pathname):
    sep = '%20'
    if pathname != None:
        cat_name = pathname.split('/')[-1]
        cat_name = cat_name.replace(sep, ' ').upper()
    return html.Div([html.H2(cat_name, style = {'textAlign': 'center', "font-weight":"bold"})])


## CATEGORY BREADCRUMB ##
@callback(
    Output("category-page-breadcrumb", "children"),
    Input("category-url", "pathname")
)
def create_breadcrumb(pathname):
    sep = '%20'
    if pathname != None:
        cat_name = pathname.split('/')[-1]
        cat_name = cat_name.replace(sep, ' ').title()
        cat_name = ' Category: ' + cat_name 
    return html.Div(
                style = {"margin": "20px 40px 0px 40px"},
                children = [
                    dbc.Breadcrumb(
                        items=[
                            {"label": "Home", "href": "/homepage", "external_link": True},
                            {"label": cat_name, "active": True},
                        ],
                        className = 'breadcrumb-item'
                    )
                ],
                className = 'breadcrumb'
            )
  

# ## PAGINATION ##
# @callback(
#     Output('all-products-pagination', 'active_page'),
#     [Input("category-url", "pathname")])
# def pagination(pathname):
#     # extract category
#     sep = '%20'
#     if pathname != None:
#         cat_name = pathname.split('/')[-1]
#         cat_name = cat_name.replace(sep, ' ').title()

#     # get original category english name in database
#     cat_name = category_dict.get(cat_name)

#     # api url
#     url = "http://127.0.0.1:5000/score_rank?category=" + cat_name

#     # get category products from api
#     r = requests.get(url)
#     data = r.text
#     all_prod = pd.read_json(data)

#     max_length = int(math.ceil(len(all_prod)/pg_size))

#     return html.Div(
#                 style = {"margin": "40px 0px"},
#                 children = [
#                     dbc.Pagination( 
#                         active_page = 1,
#                         max_value = max_length, 
#                         first_last = True, 
#                         previous_next = True, 
#                         fully_expanded = False,
#                         className = 'pagination',
#                     )
#                 ]
#             )


@callback(
    Output('clicked-button', 'children'),
    [Input('all-products-rank-score-button', 'n_clicks'),
    Input('all-products-price-button', 'n_clicks'),
    Input('all-products-top-sales-button', 'n_clicks')],
    [State('clicked-button', 'children')]
)
def updated_clicked(btn1, btn2, btn3, prev_clicks):

    prev_clicks = dict([i.split(':') for i in prev_clicks.split(' ')])
    last_clicked = 'nan'

    if btn1 > int(prev_clicks['overall']):
        last_clicked = 'overall'
    elif btn2 > int(prev_clicks['price']):
        last_clicked = 'price'
    elif btn3 > int(prev_clicks['sales']):
        last_clicked = 'sales'

    cur_clicks = 'overall:{} price:{} sales:{} last:{}'.format(btn1, btn2, btn3, last_clicked)

    return cur_clicks

## ALL PRODUCTS + PAGINATION + BUTTONS FILTER ##
@callback(
    Output('all-products-card', 'children'),
    [# Input('all-products-pagination', 'children'),
    Input('all-products-pagination', 'active_page'),
    Input('all-products-rank-score-button', 'n_clicks'),
    Input('all-products-price-button', 'n_clicks'),
    Input('all-products-top-sales-button', 'n_clicks'),
    Input("category-url", "pathname"),
    Input('clicked-button', 'children')])
def update_page(active_page, btn1, btn2, btn3, pathname, str):
    # extract category
    sep = '%20'
    if pathname != None:
        cat_name = pathname.split('/')[-1]
        cat_name = cat_name.replace(sep, ' ').title()

    # get original category english name in database
    cat_name = category_dict.get(cat_name)

    # track click
    changed_id = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    keyword = 'last:'
    before_keyword, keyword, changed_id = str.partition(keyword)

    # full data
    products = get_full_product_info(engine)
    products = products.rename({"product_id":"product id"}, axis = 1)

    if 'overall' == changed_id:
        # api url
        url = "http://backend:5001/score_rank?category=" + cat_name

        # get category products from api
        r = requests.get(url)
        data = r.text
        all_prod = pd.read_json(data)
        all_prod = pd.merge(all_prod, products, on="product id", how = "left")
    
        # adding to page
        if active_page:
            start = pg_size * (active_page-1)

            if len(all_prod) < start + pg_size:
                end = len(all_prod)
            else:
                end = pg_size * active_page
            
            if len(all_prod) < start-1:
                return html.Div(
                            children = [
                                html.H4("No more products available in this category",
                                style = { "text-align": "center"}),
                                html.A(html.H6("Back to Homepage >>", style = { "text-align": "center"}), href="/homepage")
                            ],
                            className = "container-general"
                        )
            else:
                return html.Div(
                            children = [
                                generate_product_card(all_prod.iloc[i,]) for i in range(start, end) 
                            ],
                            className = "container-product-listing"
                        )
        else:
            return html.Div(
                        children = [
                           generate_product_card(all_prod.iloc[i,]) for i in range(len(all_prod))
                        ],
                        className = "container-product-listing"
                    )
    
    elif 'price' == changed_id:
        # api url
        url = "http://backend:5001/price_rank?category=" + cat_name

        # get category products from api
        r = requests.get(url)
        data = r.text
        all_prod = pd.read_json(data)
        all_prod = pd.merge(all_prod, products, on="product id", how = "left")
    
        # adding to page
        if active_page:
            start = pg_size * (active_page-1)

            if len(all_prod) < start + pg_size:
                end = len(all_prod)
            else:
                end = pg_size * active_page
                
            if len(all_prod) < start-1:
                return html.Div(
                            children = [
                                html.H4("No more products available in this category",
                                style = { "text-align": "center"}),
                                html.A(html.H6("Back to Homepage >>", style = { "text-align": "center"}), href="/homepage")
                            ],
                            className = "container-general"
                        )
            else:
                return html.Div(
                            children = [
                                generate_product_card(all_prod.iloc[i,]) for i in range(start, end) 
                            ],
                            className = "container-product-listing"
                        )
        else:
            return html.Div(
                        children = [
                            generate_product_card(all_prod.iloc[i,]) for i in range(len(all_prod))
                        ],
                        className = "container-product-listing"
                    )

    elif 'sales' == changed_id:
        # api url
        url = "http://backend:5001/sale_rank?category=" + cat_name

        # get category products from api
        r = requests.get(url)
        data = r.text
        all_prod = pd.read_json(data)
        all_prod = pd.merge(all_prod, products, on="product id", how = "left")
    
        # adding to page
        if active_page:
            start = pg_size * (active_page-1)

            if len(all_prod) < start + pg_size:
                end = len(all_prod)
            else:
                end = pg_size * active_page
                
            if len(all_prod) < start-1:
                return html.Div(
                            children = [
                                html.H4("No more products available in this category",
                                style = { "text-align": "center"}),
                                html.A(html.H6("Back to Homepage >>", style = { "text-align": "center"}), href="/homepage")
                            ],
                            className = "container-general"
                        )
            else:
                return html.Div(
                            children = [
                                generate_product_card(all_prod.iloc[i,]) for i in range(start, end) 
                            ],
                            className = "container-product-listing"
                        )
        else:
            return html.Div(
                        children = [
                            generate_product_card(all_prod.iloc[i,]) for i in range(len(all_prod))
                        ],
                        className = "container-product-listing"
                    )

    else:
        # api url
        url = "http://backend:5001/score_rank?category=" + cat_name

        # get category products from api
        r = requests.get(url)
        data = r.text
        all_prod = pd.read_json(data)
        all_prod = pd.merge(all_prod, products, on="product id", how = "left")
    
        # adding to page
        if active_page:
            start = pg_size * (active_page-1)

            if len(all_prod) < start + pg_size:
                end = len(all_prod)
            else:
                end = pg_size * active_page
                
            if len(all_prod) < start-1:
                return html.Div(
                            children = [
                                html.H4("No more products available in this category",
                                style = { "text-align": "center"}),
                                html.A(html.H6("Back to Homepage >>", style = { "text-align": "center"}), href="/homepage")
                            ],
                            className = "container-general"
                        )
            else:
                return html.Div(
                            children = [
                                generate_product_card(all_prod.iloc[i,]) for i in range(start, end) 
                            ],
                            className = "container-product-listing"
                        )
        else:
            return html.Div(
                        children = [
                            generate_product_card(all_prod.iloc[i,]) for i in range(len(all_prod))
                        ],
                        className = "container-product-listing"
                    )



## YOU MAY ALSO LIKE ##
@callback(
    Output('ymal-products-card', 'children'),
    Input("category-url", "pathname"))
def update_you_may_also_like(pathname):
    num_of_cat = len(category_dict)-1
    num_cat_list = list(range(0, num_of_cat))
    index = random.sample(num_cat_list, 3)

    cat_list = list(category_dict.values())

    all_prod = pd.DataFrame()
    for i in index:
        cat_name_yaml = cat_list[i]

        # api url
        url = "http://backend:5001/score_rank?category=" + cat_name_yaml

        # get category products from api
        r = requests.get(url)
        data = r.text
        cat_df = pd.read_json(data)

        all_prod = pd.concat([all_prod, cat_df])
    
    products = get_full_product_info(engine)
    products = products.rename({"product_id":"product id"}, axis = 1)
    all_prod = pd.merge(all_prod, products, on="product id", how = "left")
    all_prod = all_prod.sample(frac=1, random_state=42).reset_index(drop=True)

    if len(all_prod) < 20:
        max = len(all_prod)
    else:
        max = 20

    if pathname != None:
        return html.Div(
                    children = [
                        generate_product_card(all_prod.iloc[i,]) for i in range(0, max)
                    ],
                    className = "container-product-listing-horizontal-scroll"
                )