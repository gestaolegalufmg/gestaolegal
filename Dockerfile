FROM python:3.9.5-buster
RUN apt-get update && \
    apt-get install -y nano htop && \
    mkdir /code
ENV STATIC_URL /static
ENV STATIC_PATH /code/gestaolegal
COPY . /code
WORKDIR /code
RUN pip install --upgrade pip
RUN pip install -r requirements.txt