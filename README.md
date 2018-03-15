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
docker run --name postgres -p 32769:5432 -e POSTGRES_PASSWORD=mysecretpassword -d postgres

# connect to postgres container
docker exec -it $(docker ps -aqf "name=postgres") bash

# inside docker
cat << EOF > /tmp/database.sql
CREATE DATABASE twitter_app_db;
CREATE TABLE users (
  id SERIAL,
  email VARCHAR,
  hashed_password VARCHAR,
  name CHAR(20),
  type INTEGER,
  creation_date DATE NOT NULL DEFAULT(now()),
  last_login DATE NOT NULL DEFAULT(now()),
  PRIMARY KEY (id, email)
);
EOF

# change user to postgres
su postgres

# as postres user
psql
\i /tmp/database.sql
```

deploy a postgresql database on localhost, port 32769 and run
```bash
export AWS_ACCESS_KEY_ID=<AWS ID>
export AWS_SECRET_ACCESS_KEY=<AWS SECRET>
python src/app/app.py
```
