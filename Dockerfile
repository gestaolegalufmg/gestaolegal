FROM python:3.8.8-buster
RUN apt-get update && \
    apt-get install -y nano && \
    mkdir /code
COPY . /code
WORKDIR /code
RUN pip install --upgrade pip
RUN pip install -r requirements.txt