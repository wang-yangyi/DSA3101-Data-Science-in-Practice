# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /delivery

COPY deliverypages /delivery/deliverypages
COPY delivery-pages.py delivery-pages.py
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN pip3 install PyMySQL
COPY dsa3101-class.pem dsa3101-class.pem
RUN apt-get update && apt-get install -y openssh-server
RUN chmod 600 dsa3101-class.pem
RUN ssh -o StrictHostKeyChecking=no -i dsa3101-class.pem -L 3306:13.251.201.156:3306 -N -f dsa3101@13.251.201.156

EXPOSE 8050

ENTRYPOINT ["python", "delivery-pages.py"]