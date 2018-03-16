CREATE DATABASE twitter_app_db;

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
  storage_url VARCHAR NOT NULL,
  PRIMARY KEY (id, user_id),
  FOREIGN KEY (user_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE
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
  pipeline_dataset INTEGER NOT NULL,
  pipeline_prep_stages JSONB NOT NULL,
  pipeline_models JSONB NOT NULL,
  classification_criteria INTEGER NOT NULL,
  training_status INTEGER NOT NULL DEFAULT(0),
  PRIMARY KEY (id, user_id),
  FOREIGN KEY (user_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE,
  FOREIGN KEY (pipeline_dataset) REFERENCES datasets(id)
);

CREATE TABLE preprocessing_methods (
  id SERIAL UNIQUE,
  prep_name CHAR(20),
  prep_transformation JSONB,
  PRIMARY KEY (id)
);

CREATE TABLE models (
  id SERIAL UNIQUE,
  model_name CHAR(20),
  model_properties JSONB,
  PRIMARY KEY (id)
);
