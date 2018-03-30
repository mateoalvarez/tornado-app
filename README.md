# tornado-app

Tornado web app with postgresql database to launch tensorflow pipelines

## Setup
To setup the project,

Generate folder to store dev logs in order to be able to deploy the app
``` bash
mkdir src/app/logs
```

Make sure you have installed the required libraries.
``` bash
pip install -r setup/requirements.txt
```

Deploy postgres and make sure you have created the database in postgres.
``` bash
# deploy postgres container
docker run --name postgres -p 32769:5432 -v $(pwd)/src/db/create_database.sql:/create_database.sql -e POSTGRES_PASSWORD=mysecretpassword -d postgres

# connect to postgres container
docker exec -it $(docker ps -aqf "name=postgres") bash

# inside docker
# as postres user
psql
\i /create_database.sql
```

deploy the application on localhost, on port 8888
```bash
export AWS_ACCESS_KEY_ID=<AWS ID>
export AWS_SECRET_ACCESS_KEY=<AWS SECRET>
export BUCKET_DATASET=<DATASETS_BUCKET_NAME>
export BUCKET_DATASETS_REGION=<DATASETS_BUCKET_REGION>
python src/app/app.py
```

generate a docker image

```
cd tornado-app
docker build -t image:0.1.1 .
```

deploy docker image, by default it will use region=eu-west-1. In case you want to change it, you should set an extra environment variable: -e AWS_REGION=<your_region>

```
docker run -it --rm -p 9090:8888 -e DATABASE_NAME=twitter_app_db -e DATABASE_USER=postgres -e DATABASE_PASS=mysecretpassword -e DATABASE_HOST=$(docker inspect --format '{{ .NetworkSettings.IPAddress }}' postgres) -e DATABASE_PORT=5432  -e AWS_ACCESS_KEY_ID=<aws_access_key_id> -e AWS_SECRET_ACCESS_KEY=<aws_secret_access_key> -e BUCKET_DATASET=<bucket_dataset> -e BUCKET_DATASETS_REGION=<bucket_datasets_region> --name tornado-app image:0.1.1
```

