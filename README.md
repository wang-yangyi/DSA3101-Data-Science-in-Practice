# What is this project about?
Building a recommendation system with Flask and Dash on python. Backend models and data fetching are built using Flask and made into an API. Frontend include building a dashboard or interface (using Dash) for customers to get recommendations from the models and it also involves calling API for the data. Frontend team also has to build a dashboard/interface for internal e-commerce team to track delivery status for the different packages. Dataset used: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

## Contributions to this project
- Documentations of project and how to run it (README.md)
- Dockerisation of the different components (docker-compose.yaml, requirements.txt, miscellaneous changes to backend & frontend code)
- Recommendation system frontend (dashboard-reco.py, homepage.py, style.css, assets)

# README to run project (mysql storage has been removed, project cannot be runned anymore)
Clone this repo to run the models and dash

## Running with docker-compose (Use "dockerized" branch)
Make sure you have docker-compose cli installed on your local machine and docker desktop is running

At the root directory of "dockerized" branch run
```
docker-compose up --build -d
```
This will build 3 containers at once, the reco, delivery and backend containers. (~1min)

Do wait ~30s to 1 min for all the containers to startup (the reco and delivery containers will wait for backend to finish running before it stops restarting. By default, the containers are **set to restart on failure**)

Flask api in backend container has not finish starting up hence reco and delivery contianers will fail and attempt to restart:
![](/assets/Screenshot%202022-04-14%20at%2019.41.52.png)

Backend container will always be running so check logs to see if it has finish starting up, this means flask api has not started:
![](/assets/Screenshot%202022-04-14%20at%2019.42.02.png)

To check if flask api in backend container finished starting up, in your docker-desktop click on containers -> dsa3101-2120-03-cust-backend-1. This should bring you to the container's logs and you will see "Running on http://127.0.0.1:5001" and reco and delivery containers will stop restarting.
![](/assets/Screenshot%202022-04-14%20at%2019.42.36.png)


Once all container starts running, visit the following to see the dashboards and use the api:

api:
- localhost:5001/any-get-requests-you-want

delivery dashboard:
- localhost:8050

recommendation dashbaord:
- localhost:8051

To stop and remove containers run:
```
docker-compose down rmi 
```

## Running Locally (Use "main" branch)
### Running Backend Flask API

 Use following command to open SSH tunnel on local machine:
```
ssh -i <path-to-dsa3101-class.pem> -L 3306:localhost:3306 -N -f dsa3101@13.251.201.156
```
Install all the pacakges stated in Requirements.txt using "pip install <package-name>"
 
** Note that some macOS users will face problems with the lightgbm package, use "brew install lightgbm" instead of pip. For macOS users with m1 chip, the flask api may not be able to run even after "brew install lightgbm" hence please run the application using docker-compose instead (follow the instructions above)

Running Flask (Windows):
```
cd "back-end/All_APIs"
$env:FLASK_APP = "Merged_APIs"
flask run
```

Running Flask (macOS):
```
cd "back-end/All_APIs"
export FLASK_APP=Merged_APIs
flask run
```

Test APIs:
- http://127.0.0.1:5000/orders?start_time=2017-02-28&end_time=2017-03-15&status=delivered
- http://127.0.0.1:5000/delayplotdata
- http://127.0.0.1:5000/timemodel?product_id=4244733e06e7ecb4970a6e2683c13e61&purchase_date=2022-04-06&seller_zip=01013&customer_zip=01018
- http://127.0.0.1:5000/timemodel?product_id=4244733e06e7ecb4970a6e2683c13e61&purchase_date=2022-04-04%2023:22:48&seller_zip=01013&customer_zip=01014
- http://127.0.0.1:5000/moneymodel?product_id=4244733e06e7ecb4970a6e2683c13e61&purchase_date=2022-04-06&seller_zip=01013&customer_zip=01018
- http://127.0.0.1:5000/moneymodel?product_id=4244733e06e7ecb4970a6e2683c13e61&purchase_date=2022-04-04%2023:22:48&seller_zip=01013&customer_zip=01014
- http://127.0.0.1:5000/category
- http://127.0.0.1:5000/sale_rank?category=health_beauty
- http://127.0.0.1:5000/price_rank?category=health_beauty
- http://127.0.0.1:5000/score_rank?category=health_beauty
- http://127.0.0.1:5000/overall_rank

### Running front-end dashbaords
**MAKE SURE FLASK API IS RUNNING FIRST**

Front-end dashboards sends requests to flask api to retrieve data so it will not work unless flask api is running

Recommendation dashboard:
```
cd "front-end"
python dashboard-reco.py
```
visit: 127.0.0.1:8051

Delivery dashboard:
```
cd "front-end"
python delivery-pages.py
```
visit: 127.0.0.1:8050


