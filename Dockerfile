FROM ubuntu:14.04

MAINTAINER Marina Latif <marina.latif@mssm.edu>


RUN apt-get update && apt-get install -y python3
RUN apt-get update && apt-get install -y libmysqlclient-dev
RUN apt-get update && apt-get install -y python3-pip
RUN apt-get update && apt-get install -y python3-dev


RUN pip3 install mysqlclient
RUN pip3 install numpy
RUN pip3 install pandas
RUN pip3 install Flask
RUN pip3 install sqlalchemy
RUN pip3 install flask-sqlalchemy
RUN pip3 install xlrd


RUN mkdir bionetbay
COPY Website /bionetbay
WORKDIR /bionetbay
RUN rm static/db_connection.json

ENTRYPOINT python3 __init__.py
