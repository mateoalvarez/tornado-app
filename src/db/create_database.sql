CREATE DATABASE twitter_app_db;

CREATE TABLE users (
  id SERIAL,
  email VARCHAR,
  password VARCHAR,
  name CHAR(20),
  type INTEGER,
  creation_date DATE NOT NULL DEFAULT(now()),
  last_login DATE NOT NULL DEFAULT(now()),
  PRIMARY KEY (id, email)
);
