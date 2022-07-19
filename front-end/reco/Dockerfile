# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /reco

COPY assets /reco/assets
COPY recopages /reco/recopages
COPY dashboard-reco.py dashboard-reco.py
COPY requirements.txt requirements.txt
COPY dsa3101-class.pem dsa3101-class.pem
RUN pip3 install -r requirements.txt
RUN pip3 install PyMySQL
RUN apt-get update && apt-get install -y openssh-server
RUN chmod 600 dsa3101-class.pem
RUN ssh -o StrictHostKeyChecking=no -i dsa3101-class.pem -L 3306:13.251.201.156:3306 -N -f dsa3101@13.251.201.156

EXPOSE 8051

ENTRYPOINT ["python", "dashboard-reco.py"]