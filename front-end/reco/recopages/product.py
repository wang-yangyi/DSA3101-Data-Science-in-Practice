from audioop import avg
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
import datetime


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


## ALL ORDER INFO - PRODUCT DATA - EVERY LINE IS AN ORDERED ITEM ##
def get_product_data(engine):
    statement = """SELECT order_id, order_item_id, o.product_id, answer_time, weight, length_cm, height_cm, width_cm, o.seller_id, city, shipping_limit_date, price, freight_value, review_id, score, comment_title, comment_message, creation_date, answer_time, category_name, portugese, english
                FROM olist.order_items AS o 
                LEFT JOIN olist.order_reviews AS o_re USING (order_id) 
                LEFT JOIN olist.products AS p ON (o.product_id = p.product_id) 
                LEFT JOIN olist.prod_cat_name AS n ON (p.category_name = n.portugese)
                LEFT JOIN olist.seller AS s on (o.seller_id = s.seller_id)"""
    data = as_pandas(engine.execute(statement))
    return data
data = get_product_data(engine)


## ALL PRODUCTS INFO ##
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
products = get_full_product_info(engine)
products = products.rename({"product_id":"product id"}, axis = 1)


## GET PRODUCT PRICE ##
def get_product_price(product_id, seller_id):
    subset = data.loc[(data['product_id'] == product_id) & (data['seller_id'] == seller_id)]

    list = subset['price'].tolist()
    price_list = [x for x in list if math.isnan(x) == False]

    denom = max(1, len(price_list))
    avg_price = sum(price_list) / denom

    return avg_price


## GET PRODUCT SCORE ##
def get_product_score(product_id, seller_id):
    subset = data.loc[(data['product_id'] == product_id) & (data['seller_id'] == seller_id)]

    list = subset['score'].tolist()
    rating_list = [x for x in list if math.isnan(x) == False]

    denom = max(1, len(rating_list))
    avg_score = sum(rating_list) / denom

    return avg_score

## GET PRODUCT WEIGHT ##
def get_product_weight(product_id, seller_id):
    subset = data.loc[(data['product_id'] == product_id) & (data['seller_id'] == seller_id)]
    list = subset['weight'].tolist()
    weight_list = [x for x in list if math.isnan(x) == False]
    denom = max(1, len(weight_list))
    avg = sum(weight_list) / denom
    avg = math.ceil(avg)
    return str(avg)


## GET PRODUCT LENGTH ##
def get_product_length(product_id, seller_id):
    subset = data.loc[(data['product_id'] == product_id) & (data['seller_id'] == seller_id)]
    list = subset['length_cm'].tolist()
    length_list = [x for x in list if math.isnan(x) == False]
    denom = max(1, len(length_list))
    avg = sum(length_list) / denom
    avg = math.ceil(avg)
    return str(avg)


## GET PRODUCT WIDTH ##
def get_product_width(product_id, seller_id):
    subset = data.loc[(data['product_id'] == product_id) & (data['seller_id'] == seller_id)]
    list = subset['width_cm'].tolist()
    width_list = [x for x in list if math.isnan(x) == False]
    denom = max(1, len(width_list))
    avg = sum(width_list) / denom
    avg = math.ceil(avg)
    return str(avg)


## GET PRODUCT HEIGHT ##
def get_product_height(product_id, seller_id):
    subset = data.loc[(data['product_id'] == product_id) & (data['seller_id'] == seller_id)]
    list = subset['height_cm'].tolist()
    height_list = [x for x in list if math.isnan(x) == False]
    denom = max(1, len(height_list))
    avg = sum(height_list) / denom
    avg = math.ceil(avg)
    return str(avg)


## GET PRODUCT OF ITEMS FROM SAME SELLER ##
def get_from_the_same_shop_products(product_id, seller_id):
    subset = data.loc[(data['seller_id'] == seller_id)]
    
    pid_list = subset['product_id'].tolist()
    pid_list.remove(product_id)
    pid_list = list(set(pid_list))

    pid_df = pd.DataFrame()

    if len(pid_list) == 1:
        return pid_df
    else:
        if len(pid_list) > 20:
            max = 20
        else:
            max = len(pid_list)    
        
        for i in range(0, max):
            pid = pid_list[i]
            if pid != product_id:    
                price = get_product_price(pid, seller_id)
                score = get_product_score(pid, seller_id)
                num_sold = get_num_of_product_sold(pid, seller_id)
                add = {'product id': pid, 'average price': price, 'average score': score, 'total sale': num_sold, 'seller id': seller_id}
                pid_df = pid_df.append(add, ignore_index=True)
        
    return pid_df
    

## GET NUMBER OF REVIEWS ##
def get_num_of_product_reviews(product_id, seller_id):
    subset = data.loc[(data['product_id'] == product_id) & (data['seller_id'] == seller_id)]

    list = subset['score'].tolist()
    review_list = [x for x in list if math.isnan(x) == False]

    num_review = len(review_list)

    return str(num_review)


## GET NUMBER SOLD ##
def get_num_of_product_sold(product_id, seller_id):
    subset = data.loc[(data['product_id'] == product_id) & (data['seller_id'] == seller_id)]

    list = subset['score'].tolist()
    review_list = [x for x in list if math.isnan(x) == False]

    num_review = len(review_list)

    return str(num_review)


## GET SELLER LOCATION ##
def get_seller_location(product_id, seller_id):
    subset = data.loc[(data['product_id'] == product_id) & (data['seller_id'] == seller_id)]

    list = subset['city'].tolist()
    location_list = [x for x in list if len(x) != 0]
   
    location = location_list[0].title()

    return location


## GET SELLER OVERALL RATING ##
def get_seller_overall_rating(seller_id):
    subset = data.loc[(data['seller_id'] == seller_id)]

    list = subset['score'].tolist()

    overall_rating_list = []
    for x in list:
        if math.isnan(x) == True:
            x = 0
            overall_rating_list.append(x)
        else:
            x = x
            overall_rating_list.append(x)
   
    avg_overall_rating = sum(overall_rating_list) / len(overall_rating_list)

    avg_overall_rating = '{:.2f}'.format(round(avg_overall_rating, 2))

    return avg_overall_rating


## GET RATING SCORE DISTRIBUTION ##
def get_rating_score_distribution(product_id, seller_id):
     subset = data.loc[(data['product_id'] == product_id) & (data['seller_id'] == seller_id)]

     one = len(subset.loc[(subset['score'] == 1)])
     two = len(subset.loc[(subset['score'] == 2)])
     three = len(subset.loc[(subset['score'] == 3)])
     four = len(subset.loc[(subset['score'] == 4)])
     five = len(subset.loc[(subset['score'] == 5)])

     score_dict = {'one': one, 'two': two, 'three': three, 'four': four, 'five': five}

     return score_dict


## GENERATE REVIEW CARD ##
def generate_review_card(row):

    int_score = int(row['score'])
    title = row['comment_title']
    msg = row['comment_message']

    return html.Div(
            children = [
                html.Div(
                    children = [
                        html.Div(
                            children = [
                                html.Img(src="/assets/usericon.png", style = {"max-width": "30px"})
                            ]
                        ),
                        html.Div(
                            children = [
                                html.Div(
                                    children = [
                                        html.P("Rating: ", style = {"vertical-align":"center"}),
                                        html.P(int_score, style = {"font-weight":"bold", "vertical-align":"center"}),
                                        html.P(" out of 5 ", style = {"vertical-align":"center"}),
                                    ],
                                    style = {"display":"flex", "flex-direction":"row", "justify-content": "flex-start", 
                                             "align-items":"center", "column-gap":"20px"},
                                ),
                                html.H6(title, style = {"font-weight": "bold"}),
                                html.P(msg),
                            ]
                        ),
                    ],
                    style = {"display": "flex", "align-items":"flex-start", "column-gap":"30px"}
                ),
                html.Hr()               
            ], 
            className = "review-card"
            )


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
                    # html.P("{} sold".format(sale), style = {"display": "inline-block", "text-align": "start"}),
                    # html.P("{} / 5.0".format(rating), style = {"display": "inline-block", "text-align": "end"})
                ])
            ], 
            className = "product"), 
        href="/{}/product/{}_{}by{}".format(url_category, url_pdt_name, url_pdt_id, seller))


## LAYOUT ##
layout = html.Div([

    dcc.Location(id='product-url', refresh=False),
    
    html.Div([
        html.Div([
            html.A(html.H2("Recommendation System"), href="/homepage", className='navlink')],
            className = 'nav'
        ),
        html.Div([
            dcc.Dropdown(id = "category-dropdown",
                        options = categories,
                        placeholder = "Search Category",
                        searchable = True),
            html.Div(id = "product-page-search-bar")], 
            className = 'nav'
        )
    ], 
    className = 'container-navbar'
    ),

    html.Div(id = 'product-page-breadcrumb'),
    
    # Product info here #
    html.Div(
        children = [
            html.Img(
                id="product-cat-image", 
                className = "product-info",
                style = {"width":"100%"}
            ),
            html.Div(style = {"width": "100%"}),

            html.Div(
                children = [
                    html.Div(id="product-name"),
                    
                    html.Div(
                        children = [
                            html.Div(id="product-rating"),
                            html.Div(id="product-num-of-review"),
                            html.Div(id="product-num-sold")
                        ],
                        style = {"display":"flex", "flex-direction":"row", "justify-content": "flex-start", 
                                 "align-items":"center", "column-gap":"50px"},
                    ),

                    html.Div(
                        children = [
                            html.Div(id="product-price"),
                            html.Div("Additonal shipping charges and taxes will be calculated at checkout", 
                                     style = {
                                        "color":"rgb(158, 158, 158)", "letter-spacing": "-.08rem", 
                                         "margin-bottom": "1.2rem", "margin-top": "1.2rem"})
                        ],
                        style = {"display":"flex", "flex-direction":"row", "justify-content": "flex-start", 
                                 "align-items":"center", "column-gap":"50px"},
                    ),

                    html.Div(
                        children = [
                            html.Button(
                                html.H6('-', style = {"vertical-align": "center", "text-align":"center"}), 
                                id='btn-deduct', 
                                n_clicks=0, 
                                style = {"display":"flex","align-items":"center", "width":"20px"}
                            ),
                            html.Div(id='product-quantity-selected', style = {"outline": "2px #888"}),
                            html.Button(
                                html.H6('+', style = {"vertical-align": "center", "text-align":"center"}), 
                                id='btn-add', 
                                n_clicks=0, 
                                style = {"display":"flex","align-items":"center", "width":"20px"})
                        ],
                        style = {"display":"flex", "flex-direction":"row", "justify-content": "flex-start", 
                                 "align-items":"center", "column-gap":"20px", "padding": "20px 0px 10px 0px"},
                    ),
                    
                    html.Div(
                        children = [
                            dbc.Button("Add to cart +", 
                                        style = {"color": "#FA8128", "width":"40%"},
                                        className = "product-cart-button"
                            ),
                            dbc.Button("Buy Now >",
                                        style = {"color": "#FA8128", "background-color":"#131921", "width":"40%"},
                                        className = "product-buy-now-button"
                            ),
                        ],
                        style = {"display":"flex", "column-gap": "50px","padding": "20px 0px"}
                    ),

                    html.Hr(style = {"margin":"20px 0px 20px 0px"}),

                    html.Div(
                        children = [
                            html.H5("Product information", style = {"font-weight": "bold"}),
                            html.Div(id="product-seller-location", style = {"padding": "10px 0px 0px 0px"}),
                            html.P("Product description will be inserted here. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo.",
                                    style = {"width": "90%", "align": "justify", "padding": "10px 0px 0px 0px"}
                                ),
                            html.Div(id="product-weight-dimension"),
                        ]
                    ),

                    html.Hr(style = {"margin":"15px 0px 20px 0px"}),

                    html.Div(
                        children = [
                            html.H6("Seller information", style = {"font-weight": "bold"}),
                            html.Div(    
                                children = [
                                    html.Div(id="product-seller"),
                                    html.Div(id="product-seller-overall-rating")
                                ],
                                style = {"display":"flex", "flex-direction":"row", "justify-content": "flex-start", 
                                        "align-items":"center", "column-gap":"15px", "padding": "10px 0px 10px 0px"},
                            )
                        ], 
                        style = {"margin":"10px 0px 0px 0px"}
                    ),

                    html.Hr(style = {"margin":"15px 0px 20px 0px"}),                    
                ],
                className = "product-info"
            ),
        ],
        className = "container-product-info"
    ),

    html.Div(
        id = "ratings",
        children = [
            html.Div(
                [html.H5(
                    "Ratings and Reviews", 
                    style = {"font-weight":"bold"}
                )],
            ),
            html.Div(
                children = [
                    html.Div(id="product-rating-review-score", style = {"width": "100px", "margin":"0px 50px"}),
                    html.Button(n_clicks = 0, id="btn_all", className = "product-cart-button", style = {"width": "120px"}),
                    html.Button(n_clicks = 0, id="btn_5", className = "product-cart-button", style = {"width": "120px"}),
                    html.Button(n_clicks = 0, id="btn_4", className = "product-cart-button", style = {"width": "120px"}),                   
                    html.Button(n_clicks = 0, id="btn_3", className = "product-cart-button", style = {"width": "120px"}),
                    html.Button(n_clicks = 0, id="btn_2", className = "product-cart-button", style = {"width": "120px"}),
                    html.Button(n_clicks = 0, id="btn_1", className = "product-cart-button", style = {"width": "120px"}),
                    html.Div(id = 'product-review-clicked-button', children = 'all:0 one:0 two:0 three:0 four:0 five:0 last:nan', style= {'display': 'none'})
                ],
                style = {"display": "grid", "grid-template-columns": "20% 10% 10% 10% 10% 10% 10%", "column-gap": "2%", "overflow-wrap":"inherit",
                         "padding": "30px 0px 30px 0px", "margin": "20px 0px 20px 0px", "background-color": "#fdf0e6", "border": "5px #FA8128", "align-items":"center"},                
            ),
            html.Div(id="product-review-card", style = {"padding": "30px 20px 20px 20px"}),
            dbc.Pagination(
                id = 'product-review-pagination', 
                # min_value = 1,
                active_page = 1,
                max_value = 5, 
                first_last = True, 
                previous_next = True, 
                # fully_expanded = False,
                className = 'pagination',
                style = {"margin": "0px 0px 40px 0px"}
            ) 
        ],
        className = "container-product-rating"
    ),

    html.Div(id = "product-page-other-seller-products"),

    html.Div(
        id = "product-page-other-products",
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
            
            html.Div(id="product-page-ymal-products-card"),
        ],

        className = "container-general"
    )    
], 
style = {"background-color": "#eaeded", "padding": "0px 0px 30px 0px"}
)


## CATEGORY DROPDOWN SEARCH BAR ##
@callback(
    Output("product-page-search-bar", "children"),
    Input("category-dropdown", "value")
)
def route_to_page(value):
    if value != None:
        return dcc.Location(pathname="/category/{}".format(value), id = "somethingrandom")


## PRODUCT BREADCRUMB ##
@callback(
    Output("product-page-breadcrumb", "children"),
    Input("product-url", "pathname")
)
def create_breadcrumb(pathname):
    sep = '%20'
    if pathname != None:
        cat_url = pathname.split('/')[1]
        cat_name = cat_url.replace(sep, ' ')

        product_name = pathname.split('/')[-1]
        product_name = product_name.split('_')[0]

    return html.Div(
                style = {"margin": "20px 40px 0px 40px"},
                children = [
                    dbc.Breadcrumb(
                        items=[
                            {"label": "Home", "href": "/homepage", "external_link": True},
                            {"label": "Category: {}".format(cat_name), "href": "/category/{}".format(cat_url), "external_link": True},
                            {"label": "Product: {}".format(product_name), "active": True}
                        ],
                        className = 'breadcrumb-item'
                    )
                ],
                className = 'breadcrumb'
            )

## PRODUCT IMAGE ##
@callback(
    Output("product-cat-image", "src"),
    Input("product-url", "pathname")
)
def product_image(pathname):
    sep = '%20'
    if pathname != None:
        cat_name = pathname.split('/')[1]
        cat_name = cat_name.replace(sep, '').lower()
    return "/assets/{}.jpeg".format(cat_name)


## PRODUCT PAGE TITLE ##
@callback(
    Output("product-name", "children"),
    Input("product-url", "pathname")
)
def product_name(pathname):
    sep = '%20'
    if pathname != None:
        product_name = pathname.split('/')[-1]
        product_name = product_name.split('_')[0]
        product_name = product_name.replace(sep, ' ').upper()
    return html.Div([html.H3(product_name, style = {"font-weight":"bold", "margin": "0px 0px 10px 0px"})])


## PRODUCT RATING ##
@callback(
    Output("product-rating", "children"),
    Input("product-url", "pathname")
)
def product_rating(pathname):
    keyword = 'by'
    # product_seller
    if pathname != None:
        pdt_name_id_seller = pathname.split('/')[-1]
        pdt_id_seller = pdt_name_id_seller.split('_')[-1]

        product_id, keyword, product_seller = pdt_id_seller.partition(keyword)

    rating = get_product_score(product_id, product_seller)

    rating = '{:.2f}'.format(rating)

    product_rating = rating + " / 5"

    return html.Div(
                children = [
                    html.H5(product_rating),
                    html.Img(src="/assets/ratingstar.png", style = {"width":"20px"})
                ],
                style = {"display":"flex", "flex-direction":"row", "justify-content": "flex-start", 
                        "align-items":"center", "column-gap":"10px"}
            )


## NUMBER OF PRODUCT NUMBER OF REVIEWS ##
@callback(
    Output("product-num-of-review", "children"),
    Input("product-url", "pathname")
)
def product_num_of_review(pathname):
    keyword = 'by'
    # product_seller
    if pathname != None:
        pdt_name_id_seller = pathname.split('/')[-1]
        pdt_id_seller = pdt_name_id_seller.split('_')[-1]

        product_id, keyword, product_seller = pdt_id_seller.partition(keyword)

    num_reviews = get_num_of_product_reviews(product_id, product_seller)

    num_reviews = num_reviews + " Reviews"

    return html.Div(
                children = [
                    html.H5(num_reviews)]
            )


## NUMBER OF PRODUCT SOLD ##
@callback(
    Output("product-num-sold", "children"),
    Input("product-url", "pathname")
)
def product_num_of_sold(pathname):
    keyword = 'by'
    # product_seller
    if pathname != None:
        pdt_name_id_seller = pathname.split('/')[-1]
        pdt_id_seller = pdt_name_id_seller.split('_')[-1]

        product_id, keyword, product_seller = pdt_id_seller.partition(keyword)

    num_sold = get_num_of_product_sold(product_id, product_seller)

    num_sold = num_sold + " Sold"

    return html.Div(
                children = [
                    html.H5(num_sold)]
            )

## PRODUCT PRICE ##
@callback(
    Output("product-price", "children"),
    Input("product-url", "pathname")
)
def product_price(pathname):
    keyword = 'by'
    # product_id
    if pathname != None:
        pdt_name_id_seller = pathname.split('/')[-1]
        pdt_id_seller = pdt_name_id_seller.split('_')[-1]

        product_id, keyword, product_seller = pdt_id_seller.partition(keyword)
    
    price = get_product_price(product_id, product_seller)
    price = '{:.2f}'.format(price)

    price = "$ " + price

    return html.H4(price, style = {"font-weight":"bold"})


## QUANITTY SELECTED ##
@callback(
    Output('product-quantity-selected', 'children'),
    Input('product-quantity-selected', 'children'),
    Input('btn-deduct', 'n_clicks'),
    Input('btn-add', 'n_clicks')
)
def quantity_click(qty, btn_deduct, btn_add):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if 'btn-deduct' in changed_id:
        update_qty = max(qty - 1, 1)
    elif 'btn-add' in changed_id:
        update_qty = qty + 1
    else:
        update_qty = 1
    return update_qty


## PRODUCT SELLER LOCATION ##
@callback(
    Output("product-seller-location", "children"),
    Input("product-url", "pathname")
)
def product_seller(pathname):
    keyword = 'by'
    # product_seller
    if pathname != None:
        pdt_name_id_seller = pathname.split('/')[-1]
        pdt_id_seller = pdt_name_id_seller.split('_')[-1]

        product_id, keyword, product_seller = pdt_id_seller.partition(keyword)

    location = get_seller_location(product_id, product_seller)

    return html.Div(
                children = [
                    html.P("Product ships from: "),
                    html.P(location, style = {"font-weight": "bold"})
                ],
                style = {"display":"flex", "column-gap":"10px"}
            )


## PRODUCT WEIGHT DIMENSIONS ##
@callback(
    Output("product-weight-dimension", "children"),
    Input("product-url", "pathname")
)
def product_price(pathname):
    keyword = 'by'
    # product_id
    if pathname != None:
        pdt_name_id_seller = pathname.split('/')[-1]
        pdt_id_seller = pdt_name_id_seller.split('_')[-1]

        product_id, keyword, product_seller = pdt_id_seller.partition(keyword)
    
    weight = "Weight: " + get_product_weight(product_id, product_seller) + 'g'
    length = "Length: " + get_product_length(product_id, product_seller) + 'cm'
    width = "Width: " + get_product_width(product_id, product_seller) + 'cm'
    height = "Height: " + get_product_height(product_id, product_seller) + 'cm'

    return html.Div(
                children = [
                    html.P(weight),
                    html.P(length),
                    html.P(width),
                    html.P(height)
                ],
                style = {"display":"flex", "flex-direction":"row", "justify-content": "flex-start", 
                         "align-items":"center", "column-gap":"20px", "padding": "10px 0px 10px 0px"}
            )        


## PRODUCT SELLER ##
@callback(
    Output("product-seller", "children"),
    Input("product-url", "pathname")
)
def product_seller(pathname):
    keyword = 'by'
    # product_seller
    if pathname != None:
        pdt_name_id_seller = pathname.split('/')[-1]
        pdt_id_seller = pdt_name_id_seller.split('_')[-1]

        product_id, keyword, product_seller = pdt_id_seller.partition(keyword)

    product_seller = "Seller ID: " + product_seller

    return html.P(product_seller, style = {"text-align": "center"})


## PRODUCT SELLER OVERALL RATING ##
@callback(
    Output("product-seller-overall-rating", "children"),
    Input("product-url", "pathname")
)
def product_seller_overall_rating(pathname):
    keyword = 'by'
    # product_seller
    if pathname != None:
        pdt_name_id_seller = pathname.split('/')[-1]
        pdt_id_seller = pdt_name_id_seller.split('_')[-1]

        product_id, keyword, product_seller = pdt_id_seller.partition(keyword)

    avg_overall_rating = get_seller_overall_rating(product_seller)

    return html.Div(
            children = [
                    html.P("Overall Seller Rating: "),
                    html.P(avg_overall_rating, style = {"font-weight": "bold"})
                ],
                style = {"display":"flex", "column-gap":"5px"}
            )


## PRODUCT RATING AND REVIEW STARS ##
@callback(
    Output("product-rating-review-score", "children"),
    Input("product-url", "pathname")
)
def product_rating_review_score_star(pathname):
    keyword = 'by'
    # product_seller
    if pathname != None:
        pdt_name_id_seller = pathname.split('/')[-1]
        pdt_id_seller = pdt_name_id_seller.split('_')[-1]

        product_id, keyword, product_seller = pdt_id_seller.partition(keyword)

    rating = get_product_score(product_id, product_seller)

    rating_float = '{:.1f}'.format(rating)

    return html.Div(
                children = [
                    html.H4(rating_float, style = {"font-weight":"bold"}),
                    html.P(" out of 5")
                ],
                style = {"display":"flex", "column-gap":"10px", "color": "#FA8128", "align-items": "baseline"}
            )


## PRODUCT REVIEW DISTRIBUTION ##
@callback(
    Output("btn_all", "children"),
    Input("product-url", "pathname")
)
def product_rating_review_score_star_all(pathname):
    keyword = 'by'
    # product_seller
    if pathname != None:
        pdt_name_id_seller = pathname.split('/')[-1]
        pdt_id_seller = pdt_name_id_seller.split('_')[-1]

        product_id, keyword, product_seller = pdt_id_seller.partition(keyword)

    score_dict = get_rating_score_distribution(product_id, product_seller)

    one = score_dict.get('one')
    two = score_dict.get('two')
    three = score_dict.get('three')
    four = score_dict.get('four')
    five = score_dict.get('five')
    total = one + two + three + four + five

    one = "1 Star ( " + str(one) + " )"
    two = "2 Star ( " + str(two) + " )"
    three = "3 Star ( " + str(three) + " )"
    four = "4 Star ( " + str(four) + " )"
    five = "5 Star ( " + str(five) + " )"
    total = "All ( " + str(total) + " )"

    return total

@callback(
    Output("btn_1", "children"),
    Input("product-url", "pathname")
)
def product_rating_review_score_star_1(pathname):
    keyword = 'by'
    # product_seller
    if pathname != None:
        pdt_name_id_seller = pathname.split('/')[-1]
        pdt_id_seller = pdt_name_id_seller.split('_')[-1]
        product_id, keyword, product_seller = pdt_id_seller.partition(keyword)
    score_dict = get_rating_score_distribution(product_id, product_seller)
    one = score_dict.get('one')
    one = "1 Star ( " + str(one) + " )"
    return one

@callback(
    Output("btn_2", "children"),
    Input("product-url", "pathname")
)
def product_rating_review_score_star_2(pathname):
    keyword = 'by'
    # product_seller
    if pathname != None:
        pdt_name_id_seller = pathname.split('/')[-1]
        pdt_id_seller = pdt_name_id_seller.split('_')[-1]
        product_id, keyword, product_seller = pdt_id_seller.partition(keyword)
    score_dict = get_rating_score_distribution(product_id, product_seller)
    two = score_dict.get('two')
    two = "2 Star ( " + str(two) + " )"
    return two

@callback(
    Output("btn_3", "children"),
    Input("product-url", "pathname")
)
def product_rating_review_score_star_3(pathname):
    keyword = 'by'
    # product_seller
    if pathname != None:
        pdt_name_id_seller = pathname.split('/')[-1]
        pdt_id_seller = pdt_name_id_seller.split('_')[-1]
        product_id, keyword, product_seller = pdt_id_seller.partition(keyword)
    score_dict = get_rating_score_distribution(product_id, product_seller)
    three = score_dict.get('three')
    three = "3 Star ( " + str(three) + " )"
    return three

@callback(
    Output("btn_4", "children"),
    Input("product-url", "pathname")
)
def product_rating_review_score_star_4(pathname):
    keyword = 'by'
    # product_seller
    if pathname != None:
        pdt_name_id_seller = pathname.split('/')[-1]
        pdt_id_seller = pdt_name_id_seller.split('_')[-1]
        product_id, keyword, product_seller = pdt_id_seller.partition(keyword)
    score_dict = get_rating_score_distribution(product_id, product_seller)
    four = score_dict.get('four')
    four = "4 Star ( " + str(four) + " )"
    return four

@callback(
    Output("btn_5", "children"),
    Input("product-url", "pathname")
)
def product_rating_review_score_star_5(pathname):
    keyword = 'by'
    # product_seller
    if pathname != None:
        pdt_name_id_seller = pathname.split('/')[-1]
        pdt_id_seller = pdt_name_id_seller.split('_')[-1]
        product_id, keyword, product_seller = pdt_id_seller.partition(keyword)
    score_dict = get_rating_score_distribution(product_id, product_seller)
    five = score_dict.get('five')
    five = "5 Star ( " + str(five) + " )"
    return five


## TRACK WHICH BUTTON IS CLICKED - REVIEW FILTER ##
@callback(
    Output('product-review-clicked-button', 'children'),
    [Input('btn_all', 'n_clicks'),
    Input('btn_1', 'n_clicks'),
    Input('btn_2', 'n_clicks'),
    Input('btn_3', 'n_clicks'),
    Input('btn_4', 'n_clicks'),
    Input('btn_5', 'n_clicks')],
    [State('product-review-clicked-button', 'children')]
)
def product_review_updated_clicked(btnall, btn1, btn2, btn3, btn4, btn5, prev_clicks):

    prev_clicks = dict([i.split(':') for i in prev_clicks.split(' ')])
    last_clicked = 'nan'

    if btnall > int(prev_clicks['all']):
        last_clicked = 'all'
    elif btn1 > int(prev_clicks['one']):
        last_clicked = 'one'
    elif btn2 > int(prev_clicks['two']):
        last_clicked = 'two'
    elif btn3 > int(prev_clicks['three']):
        last_clicked = 'three'
    elif btn4 > int(prev_clicks['four']):
        last_clicked = 'four'
    elif btn5 > int(prev_clicks['five']):
        last_clicked = 'five'
    
    cur_clicks = 'all:{} one:{} two:{} three:{} four:{} five:{} last:{}'.format(btnall, btn1, btn2, btn3, btn4, btn5, last_clicked)

    return cur_clicks


## REVIEW SECTION ##
## ALL PRODUCTS + PAGINATION + BUTTONS FILTER ##
@callback(
    Output('product-review-card', 'children'),
    [Input('product-review-pagination', 'active_page'),
    Input('btn_all', 'n_clicks'),
    Input('btn_1', 'n_clicks'),
    Input('btn_2', 'n_clicks'),
    Input('btn_3', 'n_clicks'),
    Input('btn_4', 'n_clicks'),
    Input('btn_5', 'n_clicks'),
    Input("product-url", "pathname"),
    Input('product-review-clicked-button', 'children')]
)
def product_all_reviews(active_page, btnall, btn1, btn2, btn3, btn4, btn5, pathname, str):
    keyword = 'by'
    if pathname != None:
        sep = '%20'
        cat_url = pathname.split('/')[1]
        cat_href = "/category/" + cat_url
        cat_name = cat_url.replace(sep, ' ')
        back_to_cat = "Back to Category: " + cat_name + '>>'
        
        pdt_name_id_seller = pathname.split('/')[-1]
        pdt_id_seller = pdt_name_id_seller.split('_')[-1]

        # product_id and product_seller
        product_id, keyword, product_seller = pdt_id_seller.partition(keyword)

    # track click
    changed_id = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    keyword = 'last:'
    before_keyword, keyword, changed_id = str.partition(keyword)

    pg_size = 8

    if 'all' == changed_id:
        all_reviews = data.loc[(data['product_id'] == product_id) & (data['seller_id'] == product_seller)]
        all_reviews = all_reviews.sort_values(by=['comment_message', 'comment_title'], ascending = False)

        if active_page:
            start = pg_size * (active_page-1)

            if len(all_reviews) < start + pg_size:
                end = len(all_reviews)
            else:
                end = pg_size * active_page
            
            if len(all_reviews) < start-1:
                return html.Div(
                            children = [
                                html.H4("End of Reviews",
                                style = { "text-align": "center"}),
                                html.A(html.H6(back_to_cat, style = { "text-align": "center"}), href=cat_href)
                            ],
                            className = "container-general"
                        )
            else:
                return [generate_review_card(all_reviews.iloc[i,]) for i in range(start, end)]
        else:
            return [generate_review_card(all_reviews.iloc[i,]) for i in range(len(all_reviews))]

    elif 'one' == changed_id:
        one_reviews = data.loc[(data['product_id'] == product_id) & (data['seller_id'] == product_seller) & (data['score'] == 1)]
        one_reviews = one_reviews.sort_values(by=['comment_message', 'comment_title'], ascending=False)

        if active_page:
            start = pg_size * (active_page-1)

            if len(one_reviews) < start + pg_size:
                end = len(one_reviews)
            else:
                end = pg_size * active_page
            
            if len(one_reviews) < start-1:
                return html.Div(
                            children = [
                                html.H4("End of Reviews",
                                style = { "text-align": "center"}),
                                html.A(html.H6(back_to_cat, style = { "text-align": "center"}), href=cat_href)
                            ],
                            className = "container-general"
                        )
            else:
                return [generate_review_card(one_reviews.iloc[i,]) for i in range(start, end)]
        else:
            return [generate_review_card(one_reviews.iloc[i,]) for i in range(len(one_reviews))]

    elif 'two' == changed_id:
        two_reviews = data.loc[(data['product_id'] == product_id) & (data['seller_id'] == product_seller) & (data['score'] == 2)]
        two_reviews = two_reviews.sort_values(by=['comment_message', 'comment_title'], ascending = False)

        if active_page:
            start = pg_size * (active_page-1)

            if len(two_reviews) < start + pg_size:
                end = len(two_reviews)
            else:
                end = pg_size * active_page
            
            if len(two_reviews) < start-1:
                return html.Div(
                            children = [
                                html.H4("End of Reviews",
                                style = { "text-align": "center"}),
                                html.A(html.H6(back_to_cat, style = { "text-align": "center"}), href=cat_href)
                            ],
                            className = "container-general"
                        )
            else:
                return [generate_review_card(two_reviews.iloc[i,]) for i in range(start, end)]
        else:
            return [generate_review_card(two_reviews.iloc[i,]) for i in range(len(two_reviews))]

    elif 'three' == changed_id:
        three_reviews = data.loc[(data['product_id'] == product_id) & (data['seller_id'] == product_seller) & (data['score'] == 3)]
        three_reviews = three_reviews.sort_values(by=['comment_message', 'comment_title'], ascending = False)

        if active_page:
            start = pg_size * (active_page-1)

            if len(three_reviews) < start + pg_size:
                end = len(three_reviews)
            else:
                end = pg_size * active_page
            
            if len(three_reviews) < start-1:
                return html.Div(
                            children = [
                                html.H4("End of Reviews",
                                style = { "text-align": "center"}),
                                html.A(html.H6(back_to_cat, style = { "text-align": "center"}), href=cat_href)
                            ],
                            className = "container-general"
                        )
            else:
                return [generate_review_card(three_reviews.iloc[i,]) for i in range(start, end)]
        else:
            return [generate_review_card(three_reviews.iloc[i,]) for i in range(len(three_reviews))]

    elif 'four' == changed_id:
        four_reviews = data.loc[(data['product_id'] == product_id) & (data['seller_id'] == product_seller) & (data['score'] == 4)]
        four_reviews = four_reviews.sort_values(by=['comment_message', 'comment_title'], ascending = False)

        if active_page:
            start = pg_size * (active_page-1)

            if len(four_reviews) < start + pg_size:
                end = len(four_reviews)
            else:
                end = pg_size * active_page
            
            if len(four_reviews) < start-1:
                return html.Div(
                            children = [
                                html.H4("End of Reviews",
                                style = { "text-align": "center"}),
                                html.A(html.H6(back_to_cat, style = { "text-align": "center"}), href=cat_href)
                            ],
                            className = "container-general"
                        )
            else:
                return [generate_review_card(four_reviews.iloc[i,]) for i in range(start, end)]
        else:
            return [generate_review_card(four_reviews.iloc[i,]) for i in range(len(four_reviews))]
    elif 'five' == changed_id:
        five_reviews = data.loc[(data['product_id'] == product_id) & (data['seller_id'] == product_seller) & (data['score'] == 5)]
        five_reviews = five_reviews.sort_values(by=['comment_message', 'comment_title'], ascending = False)

        if active_page:
            start = pg_size * (active_page-1)

            if len(five_reviews) < start + pg_size:
                end = len(five_reviews)
            else:
                end = pg_size * active_page
            
            if len(five_reviews) < start-1:
                return html.Div(
                            children = [
                                html.H4("End of Reviews",
                                style = { "text-align": "center"}),
                                html.A(html.H6(back_to_cat, style = { "text-align": "center"}), href=cat_href)
                            ],
                            className = "container-general"
                        )
            else:
                return [generate_review_card(five_reviews.iloc[i,]) for i in range(start, end)]
        else:
            return [generate_review_card(five_reviews.iloc[i,]) for i in range(len(five_reviews))]

    else:
        all_reviews = data.loc[(data['product_id'] == product_id) & (data['seller_id'] == product_seller)]
        all_reviews = all_reviews.sort_values(by=['comment_message', 'comment_title'], ascending = False)

        if active_page:
            start = pg_size * (active_page-1)

            if len(all_reviews) < start + pg_size:
                end = len(all_reviews)
            else:
                end = pg_size * active_page
            
            if len(all_reviews) < start-1:
                return html.Div(
                            children = [
                                html.H4("End of Reviews",
                                style = { "text-align": "center"}),
                                html.A(html.H6(back_to_cat, style = { "text-align": "center"}), href=cat_href)
                            ],
                            className = "container-general"
                        )
            else:
                return [generate_review_card(all_reviews.iloc[i,]) for i in range(start, end)]
        else:
            return [generate_review_card(all_reviews.iloc[i,]) for i in range(len(all_reviews))]


## FROM THE SAME SHOP ##
@callback(
    Output('product-page-other-seller-products', 'children'),
    Input("product-url", "pathname"))
def update_from_the_same_shop(pathname):
    keyword = 'by'
    # product_seller
    if pathname != None:
        pdt_name_id_seller = pathname.split('/')[-1]
        pdt_id_seller = pdt_name_id_seller.split('_')[-1]

        product_id, keyword, product_seller = pdt_id_seller.partition(keyword)
    
    shop_pid = get_from_the_same_shop_products(product_id, product_seller)

    if len(shop_pid) > 0:
        shop_prod = pd.merge(shop_pid, products, on="product id", how = "left")

        return html.Div(
                    children = [
                        html.Div(
                            style = {"grid-row":1, "margin": "0px 10px"},
                            children = [
                                html.Div(
                                    [html.H4(
                                        "FROM THE SAME SHOP", 
                                        style = {"font-weight":"bold", "color": "#FA8128"}
                                    )],
                                    style = {"margin": "20px 10px 0px 10px", "padding": "10px 0px 0px 0px"}
                                )
                            ]
                        ),
                        html.Div(
                            id="product-page-ftss-products-card",
                            children = [
                                generate_product_card(shop_prod.iloc[i,]) for i in range(0, len(shop_prod)) 
                            ],
                            className = "container-product-listing-horizontal-scroll"
                        ),
                    ],
                    style = {"margin": "0px 40px 0px 40px"},
                    className = "container-general"
                )
    else:
        return html.Div()
                

## YOU MAY ALSO LIKE ##
@callback(
    Output('product-page-ymal-products-card', 'children'),
    Input("product-url", "pathname"))
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
