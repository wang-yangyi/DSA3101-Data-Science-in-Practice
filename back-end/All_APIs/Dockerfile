# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /ALL_APIs

COPY Merged_APIs.py Merged_APIs.py
COPY Requirements.txt Requirements.txt
COPY dsa3101-class.pem dsa3101-class.pem
RUN pip3 install -r Requirements.txt
RUN pip3 install PyMySQL
RUN apt-get update && apt-get install -y --no-install-recommends apt-utils
RUN apt-get -y install curl
RUN apt-get install libgomp1
RUN apt-get update && apt-get install -y openssh-server
RUN chmod 600 dsa3101-class.pem
RUN ssh -o StrictHostKeyChecking=no -i dsa3101-class.pem -L 3306:13.251.201.156:3306 -N -f dsa3101@13.251.201.156
ENV FLASK_APP=Merged_APIs
EXPOSE 5001

ENTRYPOINT ["flask", "run", "--host=0.0.0.0", "--port=5001"] 