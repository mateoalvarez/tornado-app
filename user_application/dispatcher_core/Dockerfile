FROM python:3.6

RUN apt-get update \
    && apt-get -qq clean \
    && rm -rf /var/lib/apt/lists/*

ENV TINI_VERSION v0.17.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
RUN pip install -r requirements.txt

COPY dispatcher_core/dispatcher.py /usr/src/app/
ENTRYPOINT ["/tini", "--"]
CMD ["python", "/usr/src/app/dispatcher.py"]
