FROM python:3.6
EXPOSE 8888

RUN apt-get update

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY environment/requirements.txt /usr/src/app/
RUN pip install -r requirements.txt

COPY . /usr/src/app
