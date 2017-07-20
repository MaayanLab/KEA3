FROM ubuntu:14.04

MAINTAINER Marina Latif <marina.latif@mssm.edu>

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

ENTRYPOINT python /binder/Website/__init__.py