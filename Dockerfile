FROM ubuntu:14.04

MAINTAINER Marina Latif <marina.latif@mssm.edu>

<<<<<<< HEAD
=======
<<<<<<< HEAD

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
=======
>>>>>>> working
RUN apt-get update && apt-get install -y python
RUN apt-get update && apt-get install -y python-pip
RUN apt-get update && apt-get install -y python-dev
RUN apt-get update && apt-get install -y python-MySQLdb

RUN pip install numpy
RUN pip install pandas
RUN pip install Flask
RUN pip install sqlalchemy
RUN pip install flask-sqlalchemy

RUN mkdir binder
COPY . /binder

<<<<<<< HEAD
ENTRYPOINT python /binder/Website/__init__.py
=======
ENTRYPOINT python /binder/Website/__init__.py
>>>>>>> 7fe1b72c8dabd1d86e9f403250d22f264589eb2f
>>>>>>> working
