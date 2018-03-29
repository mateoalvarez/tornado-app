FROM python:3.6
EXPOSE 8888

RUN apt-get update \
    && apt-get -qq clean \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY setup/requirements.txt /usr/src/app/
RUN pip install -r requirements.txt

ENV TINI_VERSION v0.17.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini

COPY . /usr/src/app
ENTRYPOINT ["/tini", "--"]
CMD ["bash", "/usr/src/app/docker/entrypoint.sh"]
