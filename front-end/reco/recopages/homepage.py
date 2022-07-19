import dash
from dash import callback
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from dash.dependencies import Input, Output
import re
import requests

# Connecting to mysql
passwd = 'Y5cKZQEI'
engine = create_engine('mysql+pymysql://e0424903:' + passwd + '@13.251.201.156:3306/olist')

# convert results to dataframe
def as_pandas(results):
    columns = results.keys()
    rows = results.fetchall()
    df = pd.DataFrame(data=rows, columns=columns)
    return df

# Get list of category sorted alphabetically
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

# Get list of category sorted based on sales volume
def get_cat_volume(engine):
    statement = """SELECT c.english, COUNT(*) \
                        FROM olist.order_items o, olist.products p, olist.prod_cat_name c \
                        WHERE o.product_id = p.product_id \
                        AND p.category_name = c.portugese \
                        GROUP BY c.english \
                        ORDER BY COUNT(*) DESC"""
    cat_list = as_pandas(engine.execute(statement))
    cat_list_cleaned = cat_list['english'].map(lambda x: re.sub("(\r)","",x))
    cat_list_cleaned = cat_list_cleaned.map(lambda x: re.sub("_"," ",x).title())
    cat_options = [cat for cat in cat_list_cleaned]
    return cat_options

cat_vol = get_cat_volume(engine)

# generate buttons for each category
def generate_cat_buttons(name):
    return dbc.Button(name, className = "button", href = "/category/{}".format(name), style = {'width':"100%"})

# getting popular products from api
r = requests.get("http://backend:5001/overall_rank")
data = r.text
pop_prod = pd.read_json(data)

def get_combined_product(engine):
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

products = get_combined_product(engine)
products = products.rename({"product_id":"product id"}, axis = 1)
merged = pd.merge(pop_prod, products, on="product id", how = "left")

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

layout = html.Div([
    html.Div(children = [
        html.Div(style = { "margin": "0px 0px 20px 0px"}, children = [
            html.H2(
                "Recommendation System", 
                style = {'textAlign': 'center', "color": "white"}
            )
        ]),
        html.Div(style = { "margin": "30px 40px 10px 40px"}, children = [
            dcc.Dropdown(
                id = "cat-dropdown",
                options = categories,
                placeholder = "Search Category",
                searchable = True,
            )
        ])
    ], style = {"padding":"20px 0px 30px 0px","background-color":"#131921"}),
    
    html.Div(children = [
        html.Div([
            html.H4(
                "TRENDING CATEGORIES",
                style = { "font-weight":"bold", "color": "#FA8128", "margin": "10px 10px"}
            )
        ], style = { "grid-row":1, "margin": "20px 10px 0px 10px", "padding": "10px 0px 0px 0px" }),
        html.Div(children = [
            generate_cat_buttons(i) for i in cat_vol
        ], className = "container-cat"),
    ], className = "container-general", style = {"padding": "0px 0px 30px 0px"}),
    html.Div(children = [
        html.Div([
            html.H4(
                "POPULAR PRODUCTS",
                style = { "font-weight":"bold", "color": "#FA8128", "margin": "10px 10px"}
            )
        ], style = { "grid-row":1, "margin": "20px 10px 0px 10px", "padding": "10px 0px 0px 0px" }),
        html.Div([
            generate_product_card(merged.iloc[i,]) for i in range(len(merged))
        ], className = "container-product-listing")
    ], className = "container-general"),
    html.Div(id = "dropdownrender"),
], style = {"background-color": "#eaeded", "padding": "0px 0px 30px 0px"})

@callback(
    Output("dropdownrender", "children"),
    Input("cat-dropdown", "value")
)
def route_to_page(value):
    if value != None:
        cat_chosen = value
        return cat_chosen, dcc.Location(pathname="/category/{}".format(value), id = "somethingrandom")


