CREATE DATABASE twitter_app_db;

\connect twitter_app_db

CREATE TABLE users (
  id SERIAL UNIQUE,
  email VARCHAR,
  hashed_password VARCHAR,
  name CHAR(20),
  type INTEGER,
  creation_date DATE NOT NULL DEFAULT(now()),
  last_login DATE NOT NULL DEFAULT(now()),
  PRIMARY KEY (id, email)
);

CREATE TABLE user_settings (
  id SERIAL UNIQUE,
  user_id INTEGER NOT NULL,
  PRIMARY KEY (id, user_id),
  FOREIGN KEY (user_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE datasets (
  id SERIAL UNIQUE,
  user_id INTEGER NOT NULL,
  dataset_name VARCHAR NOT NULL,
  storage_url VARCHAR NOT NULL,
  PRIMARY KEY (id, user_id),
  FOREIGN KEY (user_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE classification_criteria (
  id SERIAL UNIQUE,
  name CHAR(20),
  properties JSONB,
  PRIMARY KEY (id)
);

CREATE TABLE engines (
  id SERIAL UNIQUE,
  engine_name CHAR(20),
  engine_configuration JSONB,
  PRIMARY KEY (id)
);

-- NOT NECESSARY FOR THE MOMENT
-- CREATE TABLE dataset_metrics (
--   id SERIAL,
--   dataset_id INTEGER NOT NULL,
--   metrics JSONB,
--   PRIMARY KEY (id, dataset_id),
--   FOREIGN KEY (dataset_id) REFERENCES datasets(id) ON UPDATE CASCADE ON DELETE CASCADE
-- );

CREATE TABLE  pipelines (
  id SERIAL UNIQUE,
  user_id INTEGER NOT NULL,
  pipeline_name CHAR(20),
  pipeline_engine INTEGER NOT NULL DEFAULT(1),
  pipeline_dataset INTEGER NOT NULL,
  pipeline_prep_stages JSONB NOT NULL,
  pipeline_models JSONB NOT NULL,
  classification_criteria INTEGER NOT NULL,
  training_status INTEGER NOT NULL DEFAULT(0),
  PRIMARY KEY (id, user_id),
  FOREIGN KEY (user_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE,
  FOREIGN KEY (pipeline_dataset) REFERENCES datasets(id),
  FOREIGN KEY (pipeline_engine) REFERENCES engines(id),
  FOREIGN KEY (classification_criteria) REFERENCES classification_criteria(id)
);

CREATE TABLE preprocessing_methods (
  id SERIAL UNIQUE,
  prep_name CHAR(20),
  prep_engine INTEGER NOT NULL DEFAULT(1),
  prep_transformation JSONB,
  PRIMARY KEY (id),
  FOREIGN KEY (prep_engine) REFERENCES engines(id)
);

CREATE TABLE models (
  id SERIAL UNIQUE,
  model_name CHAR(20),
  model_engine INTEGER NOT NULL DEFAULT(1),
  model_properties JSONB,
  PRIMARY KEY (id),
  FOREIGN KEY (model_engine) REFERENCES engines(id)
);
