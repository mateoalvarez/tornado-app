FROM combustml/mleap-serving:0.8.0

RUN apt-get update \
    && apt-get install -y -qq --no-install-recommends \
    netcat \
    && apt-get -qq clean \
    && rm -rf /var/lib/apt/lists/*

ADD https://s3.eu-central-1.amazonaws.com/tornado-app-emr/docker-dependencies/mleap-runtime_2.11-0.8.1-pyxis-version.jar /opt/docker/lib/mleap-runtime_2.11-0.8.1-pyxis-version.jar
ADD https://s3.eu-central-1.amazonaws.com/tornado-app-emr/docker-dependencies/mleap-base_2.11-0.8.1-pyxis-version.jar /opt/docker/lib/mleap-base_2.11-0.8.1-pyxis-version.jar
ADD https://s3.eu-central-1.amazonaws.com/tornado-app-emr/docker-dependencies/mleap-core_2.11-0.8.1-pyxis-version.jar /opt/docker/lib/mleap-core_2.11-0.8.1-pyxis-version.jar
ADD https://s3.eu-central-1.amazonaws.com/tornado-app-emr/docker-dependencies/bundle-ml_2.11-0.8.1-pyxis-version.jar /opt/docker/lib/bundle-ml_2.11-0.8.1-pyxis-version.jar
ADD https://s3.eu-central-1.amazonaws.com/tornado-app-emr/docker-dependencies/stanford-corenlp-3.9.1.jar /opt/docker/lib/stanford-corenlp-3.9.1.jar
ADD https://s3.eu-central-1.amazonaws.com/tornado-app-emr/docker-dependencies/stanford-corenlp-3.9.1-models-english.jar /opt/docker/lib/stanford-corenlp-3.9.1-models-english.jar
ADD https://s3.eu-central-1.amazonaws.com/tornado-app-emr/docker-dependencies/stanford-corenlp-3.9.1-models-spanish.jar /opt/docker/lib/stanford-corenlp-3.9.1-models-spanish.jar
ADD https://s3.eu-central-1.amazonaws.com/tornado-app-emr/docker-dependencies/mleap-serving_2.11-0.8.1-pyxis-version.jar /opt/docker/lib/mleap-serving_2.11-0.8.1-pyxis-version.jar

ADD docker/mleap-serving /opt/docker/bin/mleap-serving
