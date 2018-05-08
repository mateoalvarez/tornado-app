FROM combustml/mleap-serving:0.8.0

RUN apt-get update \
    && apt-get install -y -qq --no-install-recommends \
    netcat \
    && apt-get -qq clean \
    && rm -rf /var/lib/apt/lists/*

ADD docker/mleap-serving /opt/docker/bin/mleap-serving
