#!/usr/bin/env bash

: ${AWS_ACCESS_KEY_ID:?"Need to set AWS_ACCESS_KEY_ID in order to stablish correctly the connection to AWS backend."}
: ${AWS_SECRET_ACCESS_KEY:?"Need to set AWS_SECRET_ACCESS_KEY in order to stablish correctly the connection to AWS backend."}


if [ -z ${DATABASE_NAME} ]; then
    echo "DATABASE_NAME is not set, default value will be used."
fi

if [ -z ${DATABASE_USER} ]; then
    echo "DATABASE_USER is not set, default value will be used."
fi

if [ -z ${DATABASE_PASS} ]; then
    echo "DATABASE_PASS is not set, default value will be used."
fi

if [ -z ${DATABASE_HOST} ]; then
    echo "DATABASE_HOST is not set, default value will be used."
fi

if [ -z ${DATABASE_PORT} ]; then
    echo "DATABASE_PORT is not set, default value will be used."
fi

if [ -z ${BUCKET_DATASET} ]; then
    echo "BUCKET_DATASET is not set, default value will be used."
fi

if [ -z ${BUCKET_DATASETS_REGION} ]; then
    echo "BUCKET_DATASETS_REGION is not set, default value will be used."
fi

if [ -z ${BUCKET_SPARK_JOBS} ]; then
    echo "BUCKET_SPARK_JOBS is not set, default value will be used."
fi

if [ -z ${BUCKET_SPARK_JOBS_REGION} ]; then
    echo "BUCKET_SPARK_JOBS_REGION is not set, default value will be used."
fi

AWS_REGION=${AWS_REGION:-"eu-west-1"}

mkdir ~/.aws/

cat > ~/.aws/credentials << EOF
[default]
aws_access_key_id = ${AWS_ACCESS_KEY_ID}
aws_secret_access_key = ${AWS_SECRET_ACCESS_KEY}
EOF

cat > ~/.aws/config << EOF
[default]
region=${AWS_REGION}
EOF

unset AWS_ACCESS_KEY_ID
unset AWS_SECRET_ACCESS_KEY

python /usr/src/app/src/app/app.py