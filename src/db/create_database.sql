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

CREATE TABLE user_settings (
  id SERIAL,
  user_id INTEGER NOT NULL,
  PRIMARY KEY (id, user_id),
  FOREIGN KEY (user_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE datasets (
  id SERIAL,
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

CREATE TABLE  (

);
