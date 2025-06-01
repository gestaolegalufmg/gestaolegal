FROM python:3.11.3-buster
RUN apt-get update && \
    apt-get install -y nano htop build-essential libssl-dev libffi-dev python-dev && \
    mkdir /code
ENV STATIC_URL /static
ENV STATIC_PATH /code/gestaolegal
COPY . /code
WORKDIR /code
RUN pip install --upgrade pip
RUN pip install .
