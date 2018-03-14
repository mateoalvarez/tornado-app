CREATE DATABASE twitter_app_db;

CREATE TABLE users (
  id SERIAL,
  email VARCHAR,
  password VARCHAR,
  name CHAR(20),
  type INTEGER,
  creation_date DATETIME NOT NULL DEFAULT(GETDATE()),
  last_login DATETIME NOT NULL DEFAULT(GETDATE()),
  PRIMARY KEY (id, email)
);
