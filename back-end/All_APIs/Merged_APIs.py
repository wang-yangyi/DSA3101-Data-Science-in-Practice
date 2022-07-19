### Merged APIs

### This file contains all the APIs available on 2022/4/5 by Group-03 Modelling Teams

######### Set Up the environment

from flask import Flask, request, jsonify, send_file, render_template
import numpy as np
import pandas as pd
from sklearn import preprocessing
import calendar

import sqlalchemy
from sqlalchemy import create_engine, inspect, select, text, and_, or_, func
from sqlalchemy import Table, MetaData
from datetime import datetime

import json

from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from lightgbm import LGBMClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report

######### Connect to database
passwd = 'FyZSMAiH'
w_engine = create_engine('mysql+pymysql://e0376935:' + passwd + '@13.251.201.156:3306/olist', echo=True)

############### Delayed Data API Funcs

m2 = MetaData(bind=w_engine)
m2.reflect()

orders = Table("orders", m2, autoload=True)

# Get daily delays
time_list = []
delay_list = []

# Year 2016
for i in range(10,13):
    for j in range(1,calendar.monthrange(2016, i)[1]+1):
        current = "2016-" + str(i) + "-" + str(j)
        stmt2 = select(func.count()).\
            where(orders.c.delivered_customer >= current).\
            where(orders.c.estimated_delivery < current)

        with w_engine.connect() as con:
            d2 = con.execute(stmt2)

        s2 = d2.fetchall()
        time_list.append("2016-" + str(i) + "-" + str(j))
        delay_list.append(s2[0][0])

# Year 2017
for i in range(1,13):
    for j in range(1,calendar.monthrange(2017, i)[1]+1):
        current = "2017-" + str(i) + "-" + str(j)
        stmt2 = select(func.count()).\
            where(orders.c.delivered_customer >= current).\
            where(orders.c.estimated_delivery < current)

        with w_engine.connect() as con:
            d2 = con.execute(stmt2)

        s2 = d2.fetchall()
        time_list.append("2017-" + str(i) + "-" + str(j))
        delay_list.append(s2[0][0])

# Year 2018
for i in range(1,9):
    for j in range(1,calendar.monthrange(2018, i)[1]+1):
        current = "2018-" + str(i) + "-" + str(j)
        stmt2 = select(func.count()).\
            where(orders.c.delivered_customer >= current).\
            where(orders.c.estimated_delivery < current)

        with w_engine.connect() as con:
            d2 = con.execute(stmt2)

        s2 = d2.fetchall()
        time_list.append("2018-" + str(i) + "-" + str(j))
        delay_list.append(s2[0][0])





############### Order Filter API Funcs

def select_orders(start_time, end_time, status):
    start_datetime = datetime.strptime(start_time, '%Y-%m-%d')
    end_datetime = datetime.strptime(end_time, '%Y-%m-%d')

    query1 = select([orders]).\
        where(orders.c.order_status == status).\
        where(orders.c.purchase_time > start_datetime).\
        where(orders.c.purchase_time < end_datetime).\
        order_by(orders.c.purchase_time)
    
    with w_engine.connect() as con:
        d1 = con.execute(query1)
    
    return d1.fetchall()




############### Estimate Freight Money Model API Funcs

#### Input processing

def product_process(product_id):
    #### 根据id获得物品信息
    #passwd = '7y5DihzG'
    #w_engine = create_engine('mysql+pymysql://e0376959:' + passwd + '@ec2-13-251-201-156.ap-southeast-1.compute.amazonaws.com/olist', echo=True)
    passwd = 'FyZSMAiH'
    w_engine = create_engine('mysql+pymysql://e0376935:' + passwd + '@13.251.201.156:3306/olist', echo=True)

    mysql = "SELECT weight, length_cm, height_cm, width_cm FROM olist.products WHERE product_id = %s;"

    conn = w_engine.connect()
    temp = conn.execute(mysql, product_id)
    temp = temp.fetchall()

    weight = temp[0][0]
    hacim = temp[0][1]*temp[0][2]*temp[0][3]

    return weight, hacim

def zip_get(zip_code):
    #### 根据id获得物品信息
    #passwd = '7y5DihzG'
    #w_engine = create_engine('mysql+pymysql://e0376959:' + passwd + '@ec2-13-251-201-156.ap-southeast-1.compute.amazonaws.com/olist', echo=True)
    passwd = 'FyZSMAiH'
    w_engine = create_engine('mysql+pymysql://e0376935:' + passwd + '@13.251.201.156:3306/olist', echo=True)

    mysql = "SELECT latitude,longitude FROM olist.geo_avg WHERE zip_code = %s;"

    conn = w_engine.connect()
    temp = conn.execute(mysql, zip_code)
    temp = temp.fetchall()

    return temp[0][0],temp[0][1]


def only_one_product(data):
    print(f"Shape Before Single Product Filtering: {data.shape}")
    # Orders with only one product
    index = data["order_id"].value_counts()[data["order_id"].value_counts() == 1].index

    data = data[data.order_id.isin(index)]
    data.reset_index(drop=True, inplace=True)
    print(f"Shape After Single Product Filtering: {data.shape}\n")
    return data


def data_input_preprocess():

    ### Connecting to Database using my password
    #passwd = '7y5DihzG'
    #w_engine = create_engine('mysql+pymysql://e0376959:' + passwd + '@ec2-13-251-201-156.ap-southeast-1.compute.amazonaws.com/olist', echo=True)
    passwd = 'FyZSMAiH'
    w_engine = create_engine('mysql+pymysql://e0376935:' + passwd + '@13.251.201.156:3306/olist', echo=True)

    ### input data and preprocess
    mysql = "SELECT OO.order_id, OP.product_id, OI.seller_id , OO.customer_id, purchase_time, approval_time, delivered_carrier, delivered_customer,estimated_delivery, weight, length_cm, height_cm, width_cm, seller_latitude, seller_longitude, customer_latitude, customer_longitude, freight_value FROM olist.order_items AS OI LEFT JOIN olist.orders AS OO ON OI.order_id = OO.order_id LEFT JOIN olist.products AS OP ON OI.product_id = OP.product_id LEFT JOIN (SELECT seller_id, latitude as seller_latitude, longitude as seller_longitude FROM olist.seller AS OS LEFT JOIN olist.geo_avg AS OG ON OS.zip_code = OG.zip_code) AS seller_loc ON seller_loc.seller_id = OI.seller_id LEFT JOIN (SELECT customer_id, latitude as customer_latitude, longitude as customer_longitude FROM olist.customers AS OC LEFT JOIN olist.geo_avg AS OG ON OC.zip_code = OG.zip_code) AS customer_loc ON customer_loc.customer_id = OO.customer_id WHERE order_status = 'delivered' AND purchase_time <> 0 AND approval_time <> 0 AND delivered_carrier <> 0 AND delivered_customer <> 0 AND estimated_delivery <> 0 AND freight_value <> 0 AND seller_latitude IS NOT NULL AND customer_latitude IS NOT NULL; "
    conn = w_engine.connect()
    temp = conn.execute(statement=mysql)
    temp = temp.fetchall()

    ### Convert to a dataframe
    data_pre = pd.DataFrame.from_records(temp)
    data_pre.columns = temp[0].keys()
    print(data_pre.head())

    ### Changing the data format

    for col in data_pre.columns[4:9]:
        data_pre[col] = pd.to_datetime(data_pre[col])
    
    data_pre['freight_value'] = pd.to_numeric(data_pre['freight_value'])

    ### Remove missing values
    data_pre = data_pre.dropna()
    data_pre.reset_index(drop=True, inplace=True)

    ### Delet orders with only one product
    data_pre = only_one_product(data_pre)


    return data_pre

def f_engineering():

    data = data_input_preprocess()

    # Volume of products
    data["hacim"] = data["length_cm"] * data["height_cm"] * data["width_cm"]

    data["purchase_month"] = data["purchase_time"].apply(lambda x: x.month)


    # Time taken from order to reach the customer (in days)
    data["order_completion_day"] = [
        (pd.to_datetime(d.strftime("%Y-%m-%d")) - pd.to_datetime(t.strftime("%Y-%m-%d"))).days
        for d, t in zip(data["delivered_customer"], data["purchase_time"])]

    # Euclidean distances between seller and customer
    data["euclidean_distance"] = (np.sqrt(((data["customer_latitude"] - data["seller_latitude"]) ** 2) +
                                          ((data["customer_longitude"] - data["seller_longitude"]) ** 2)))
    
    return data

def target_freight_variable_tags():

    data = f_engineering()
    data.loc[data["freight_value"] >= 50, "target"] = "50+"

    data.loc[(10> data["freight_value"]) & (data["freight_value"] >=0), "target"] = "0-10"

    data.loc[(20> data["freight_value"]) & (data["freight_value"] >=10), "target"] = "10-20"

    data.loc[(30> data["freight_value"]) & (data["freight_value"] >=20), "target"] = "20-30"

    data.loc[(50> data["freight_value"]) & (data["freight_value"] >=30), "target"] = "30-50"
    

    data["freight_value"] = [str(i) for i in data["freight_value"]]
    data = data[~(data["freight_value"] == "nan")]
    data.reset_index(drop=True, inplace=True)

    return data


#### Model


def freight_model():

    data = target_freight_variable_tags()

    train, test = train_test_split(data, random_state=55, test_size=0.20)
    X_train = train[["weight", "hacim",  "purchase_month", "euclidean_distance"]]
    y_train = train["target"]
    X_test = test[["weight", "hacim", "purchase_month","euclidean_distance"]]
    y_test = test["target"]

    return LGBMClassifier(random_state=55).fit(X_train,y_train)

def freight_predict(weight, hacim, purchase_month, euclidean_distance):
    finalmodel = freight_model()
    result = finalmodel.predict([[weight, hacim, purchase_month, euclidean_distance]])

    return result




############### Estimate Time Model API Funcs


def target_date_variable_tags():

    data = f_engineering()
    data.loc[data["order_completion_day"] >= 30, "target"] = "30+"

    data.loc[(3> data["order_completion_day"]) & (data["order_completion_day"] >=1), "target"] = "1-3"

    data.loc[(9> data["order_completion_day"]) & (data["order_completion_day"] >=4), "target"] = "4-9"

    data.loc[(15> data["order_completion_day"]) & (data["order_completion_day"] >=10), "target"] = "10-15"

    data.loc[(30> data["order_completion_day"]) & (data["order_completion_day"] >=16), "target"] = "16-30"
    

    data["target"] = [str(i) for i in data["target"]]
    data = data[~(data["target"] == "nan")]
    data.reset_index(drop=True, inplace=True)

    return data


#### Model


def date_model():

    data = target_date_variable_tags()

    train, test = train_test_split(data, random_state=55, test_size=0.20)
    X_train = train[["weight", "hacim",  "purchase_month", "euclidean_distance"]]
    y_train = train["target"]
    X_test = test[["weight", "hacim", "purchase_month","euclidean_distance"]]
    y_test = test["target"]

    return LGBMClassifier(random_state=55).fit(X_train,y_train)

def date_predict(weight, hacim, purchase_month, euclidean_distance):
    finalmodel = date_model()
    result = finalmodel.predict([[weight, hacim, purchase_month, euclidean_distance]])

    return result


############### Recommendation System API Funcs

def order_category():
    query = """select n.english, count(*) 
    from order_items as o 
    inner join products as p on(o.product_id = p.product_id)
    inner join prod_cat_name as n on (p.category_name = n.portugese) 
    group by n.english order by count(*) desc;"""
    with w_engine.connect() as con:
        query_re_ca = con.execute(query)
    re_category = query_re_ca.fetchall()
    t = []
    # t
    for i in range(len(re_category)):
        # tt = re_category[i][0]
        t.append(re_category[i][0][:-1])
    return t
    

def rank_sale(category):
    
    category = category + "%"

    q1="SELECT  o.product_id,  avg(score) as avg_rank, avg(price) as avg_price, sum(order_item_id) as total_sale, count(o_re.review_id) as total_review, o.seller_id From order_items as o left join order_reviews as o_re using(order_id) LEFT JOIN products AS p ON (o.product_id = p.product_id) LEFT JOIN prod_cat_name AS n ON (p.category_name = n.portugese) WHERE n.english LIKE :search_key group by product_id , seller_id order by count(*) desc;"
    
    with w_engine.connect() as con:
       rs = con.execute(text(q1).bindparams(search_key=category))
     
    s1= rs.fetchall()
  
    return s1


def rank_price(category):
    
    q = """SELECT 
                o.product_id, avg(score) as avg_rank, avg(price) as avg_price, sum(order_item_id) as total_sale, count(o_re.review_id) as total_review, o.seller_id
            FROM
                order_items AS o
                    LEFT JOIN
                order_reviews AS o_re USING (order_id)
                    LEFT JOIN
                products AS p ON (o.product_id = p.product_id)
                    LEFT JOIN
                prod_cat_name AS n ON (p.category_name = n.portugese)
            WHERE
                n.english LIKE :search_key
            GROUP BY product_id , seller_id
            ORDER BY avg_price;"""
    
    category = category + "%"
    with w_engine.connect() as con:
        rs = con.execute(text(q).bindparams(search_key = category))
        s1 = rs.fetchall()
   
    return s1

def rank_score(category):
    q = """SELECT 
                o.product_id, avg(score) as avg_rank, avg(price) as avg_price, sum(order_item_id) as total_sale, count(o_re.review_id) as total_review, o.seller_id
            FROM
                order_items AS o
                    LEFT JOIN
                order_reviews AS o_re USING (order_id)
                    LEFT JOIN
                products AS p ON (o.product_id = p.product_id)
                    LEFT JOIN
                prod_cat_name AS n ON (p.category_name = n.portugese)
            WHERE
                n.english LIKE :search_key
            GROUP BY product_id , seller_id
            ORDER BY avg_rank DESC;"""
    
    category = category + "%"
    with w_engine.connect() as con:
        rs = con.execute(text(q).bindparams(search_key = category))

    s1 = rs.fetchall()
 
    return s1
    
def product_rank():
    # get result from SQL
    q = """select o.product_id, avg(score) as avg_rank, avg(price) as avg_price, sum(order_item_id) as total_sale, count(o_re.review_id) as total_review,o.seller_id as seller_id, n.english as product_category
    from order_items as o left join order_reviews as o_re using(order_id) 
    left join products as p on(o.product_id = p.product_id)
    LEFT JOIN
    prod_cat_name AS n ON (p.category_name = n.portugese)
    group by o.product_id,o.seller_id, n.english;"""
    with w_engine.connect() as con:
        d1 = con.execute(q)
    s1 = d1.fetchall()
    s1 = pd.DataFrame(s1)
    
    # rename the dataframe
    s1.rename(columns={"product_id": "product_id", "avg_rank": "avg_score", "avg_price": "avg_price", "total_sale": "total_sale", "total_review": "total_review", "seller_id":"seller_id", "product_category": "category"}, errors="raise", inplace = True)
    
    # processing the result
    s1[["avg_score","avg_price", "total_sale"]] = s1[["avg_score","avg_price", "total_sale"]].astype('float')
    s1[["avg_price_scale", "total_sale_score_scale"]] = np.log10(s1[["avg_price", "total_sale"]])
    scaler = preprocessing.MinMaxScaler()
    s1[["avg_score_scale","avg_price_scale", "total_sale_scale"]] = scaler.fit_transform(s1[["avg_score","avg_price", "total_sale"]])
    
    #generate the total scoreing
    s1["total ranking"] = 0.2* s1["total_sale_scale"] -0.2* s1["avg_price_scale"] + 0.7 * s1["avg_score_scale"]
    s1.sort_values(by = ["total ranking"],ascending=False, inplace = True)
    
    
    return s1[:10]







######### Available APIs

app = Flask(__name__)

# Delay data
# This API should return a dictionary of time & delays in each day from "2016-10-01" to "2018-8-31"
# Can consider using this data to create a plot using plotly in dash/shiny
@app.route("/delayplotdata", methods=["GET"])
def delay_plot_data():
    dic = {"time_list":time_list, "delay_list":delay_list}

    return dic


# Order Filter
# This API should return a list containing orders from one time to another
# "status" argument determines the order is "delivered" ot "cancelled" etc.
@app.route("/orders", methods=["GET"])
def order_filter():
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    status = request.args.get('status')

    s1 = select_orders(start_time, end_time, status)

    c1,c2,c3,c4,c5,c6,c7,c8 = [],[],[],[],[],[],[],[]

    for i in range(len(s1)):
        c1.append(s1[i][0])
        c2.append(s1[i][1])
        c3.append(s1[i][2])
        c4.append(s1[i][3])
        c5.append(s1[i][4])
        c6.append(s1[i][5])
        c7.append(s1[i][6])
        c8.append(s1[i][7])

    dic = {"order_id":c1,"customer_id":c2,"order_status":c3,"purchase_time":c4,"approval_time":c5,
    "delivered_carrier":c6,"delivered_customer":c7,"estimated_delivery":c8}

    return dic

# Estimate Freight Money Model
# This API should return the estimated freight money for a given item
@app.route("/moneymodel", methods=["GET"])
def money_model():
    product_info = request.args.get('product_id')
    purchase_date = request.args.get('purchase_date')
    seller_loc = request.args.get('seller_zip')
    customer_loc = request.args.get('customer_zip')

    weight, hacim = product_process(product_info)
    seller_lat, seller_lng = zip_get(seller_loc)
    customer_lat, customer_lng = zip_get(customer_loc)

    euclidean_distance = (np.sqrt(((customer_lat- customer_lng) ** 2) +
                                          ((seller_lat - seller_lng) ** 2)))
    purchase_month = int(purchase_date[5:7])

    result = freight_predict(weight, hacim, purchase_month, euclidean_distance)

    return result[0]

# Estimate time model
# This API should return estimated time for a full delivery process
@app.route("/timemodel", methods=["GET"])
def time_model():
    product_info = request.args.get('product_id')
    purchase_date = request.args.get('purchase_date')
    seller_loc = request.args.get('seller_zip')
    customer_loc = request.args.get('customer_zip')

    weight, hacim = product_process(product_info)
    seller_lat, seller_lng = zip_get(seller_loc)
    customer_lat, customer_lng = zip_get(customer_loc)

    euclidean_distance = (np.sqrt(((customer_lat- customer_lng) ** 2) +
                                          ((seller_lat - seller_lng) ** 2)))
    purchase_month = int(purchase_date[5:7])

    result = date_predict(weight, hacim, purchase_month, euclidean_distance)

    return result[0]

# Ordered category API
# This API should return a dictionary from the most popular category to the least.
@app.route("/category")
def category():
    dic = {"category": order_category()}

    # r = order_category()
    return dic

# Sales Rank API
# This API should return the products under a given catagory ordered from the largest total sales to the lowest.
@app.route("/sale_rank", methods=["GET"])
def sale():
    category= request.args.get('category')
    
    s1 = rank_sale(category)

    c1,c2,c3,c4,c5,c6= [],[],[],[],[],[]

    for i in range(len(s1)):
        c1.append(s1[i][0])
        c2.append(s1[i][1])
        c3.append(s1[i][2])
        c4.append(s1[i][3])
        c5.append(s1[i][4])
        c6.append(s1[i][5])
        
    dic = {"product id":c1,"average score": c2, "average price":c3, "total sale" : c4, "total review":c5,"seller info": c6}

    return dic


# Price Rank API
# This API should return the products under a given catagory ordered from the lowest price to the highest.
@app.route("/price_rank", methods=["GET"])
def price_rank():
    category= request.args.get('category')
    
    s1 = rank_price(category)

    c1,c2,c3,c4,c5,c6= [],[],[],[],[],[]

    for i in range(len(s1)):
        c1.append(s1[i][0])
        c2.append(s1[i][1])
        c3.append(s1[i][2])
        c4.append(s1[i][3])
        c5.append(s1[i][4])
        c6.append(s1[i][5])
        
    dic = {"product id":c1,"average score": c2, "average price":c3, "total sale" : c4, "total review":c5,"seller info": c6}

    return dic

# Score Rank API
# This API should return a list containing products with overall rating under given category
@app.route("/score_rank", methods=["GET"])
def score_rank():
    category= request.args.get('category')

    c1,c2,c3,c4,c5,c6= [],[],[],[],[],[]
    
    s1 = rank_score(category)
    for i in range(len(s1)):
        c1.append(s1[i][0])
        c2.append(s1[i][1])
        c3.append(s1[i][2])
        c4.append(s1[i][3])
        c5.append(s1[i][4])
        c6.append(s1[i][5])
        
    dic = {"product id":c1,"average score": c2, "average price":c3, "total sale" : c4, "total review":c5,"seller info": c6}

    return dic

# Overall Rank API
# This API should return a list containing products with highest overall rating (based on price,sale,score)
@app.route("/overall_rank", methods=["GET"])
def overall_rank():
    
    s1 = product_rank()
    t = s1["category"].apply(lambda x : x[:-1]) 

    dic = {"product id":list(s1['product_id'].values),"average score": list(s1['avg_score'].values), "average price":s1['avg_price'].to_list(),
           "total sale" : s1['total_sale'].to_list(), "total review":s1['total_review'].to_list(),"seller id":list(s1['seller_id'].values), "category":list(t.values) }

    return dic