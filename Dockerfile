FROM python:3.6
EXPOSE 8888

RUN apt-get update \
    && apt-get -qq clean \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY setup/requirements.txt /usr/src/app/
RUN pip install -r requirements.txt

COPY . /usr/src/app
