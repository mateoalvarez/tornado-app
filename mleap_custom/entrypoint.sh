#!/usr/bin/env bash

# wget -P /models/ https://s3.eu-central-1.amazonaws.com/tornado-app-emr/user_1/application_3/models/preprocessing.zip
# ./docker-entrypoint.sh

# curl -XPUT -H "content-type: application/json" \
#   -d '{"path":"https://s3.eu-central-1.amazonaws.com/tornado-app-emr/user_1/application_3/artifacts/preprocessing.zip"}' \
#   http://localhost:65327/model
#
# curl -XPUT -H "content-type: application/json" \
#   -d '{"path":"/models/*"}' \
#   http://localhost:65327/model
#
# https://s3.eu-central-1.amazonaws.com/tornado-app-emr/user_1/application_3/artifacts/preprocessing.zip
