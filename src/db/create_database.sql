CREATE DATABASE twitter_app_db;
CREATE TYPE application_status_enum AS ENUM ('untrained', 'training', 'trained', 'running', 'stopped', 'error');
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

CREATE TABLE datasource_settings (
  id SERIAL UNIQUE,
  user_id INTEGER NOT NULL,
  type INTEGER NOT NULL DEFAULT(1),
  datasource_access_settings JSONB,
  PRIMARY KEY (id, user_id),
  FOREIGN KEY (user_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE datasets (
  id SERIAL UNIQUE,
  user_id INTEGER NOT NULL,
  dataset_name VARCHAR NOT NULL,
  storage_url VARCHAR NOT NULL,
  dataset_description TEXT,
  dataset_properties JSONB, -- {columns:# , rows:# , labels:# }
  PRIMARY KEY (id, user_id),
  FOREIGN KEY (user_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE engines (
  id SERIAL UNIQUE,
  engine_name CHAR(20),
  engine_configuration JSONB,
  PRIMARY KEY (id)
);

-- Templates for models

CREATE TABLE code_block_templates (
  id  SERIAL UNIQUE,
  template_name CHAR(20),
  model_engine INTEGER NOT NULL DEFAULT(1),
  code_content JSONB,
  PRIMARY KEY (id),
  FOREIGN KEY (model_engine) REFERENCES engines(id)
);

-- Block codes for users

CREATE TABLE code_block (
  id SERIAL UNIQUE,
  user_id INTEGER NOT NULL,
  code_block_template_id INTEGER NOT NULL,
  code_content JSONB,
  PRIMARY KEY (id),
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (code_block_template_id) REFERENCES code_block_templates(id)
);

CREATE TABLE classification_criteria (
  id SERIAL UNIQUE,
  name CHAR(20),
  properties JSONB,
  PRIMARY KEY (id)
);

CREATE TABLE datasource_configurations (
  id SERIAL UNIQUE,
  datasource_settings_id INTEGER NOT NULL,
  datasource_application_config JSONB,
  PRIMARY KEY (id),
  FOREIGN KEY (datasource_settings_id) REFERENCES datasource_settings(id)
);

CREATE TABLE  applications (
  id SERIAL UNIQUE,
  user_id INTEGER NOT NULL,
  application_name CHAR(20),
  training_config_resources JSONB,
  application_dataset INTEGER NOT NULL,
  application_prep_stages_ids INTEGER ARRAY NOT NULL,
  application_models_ids INTEGER ARRAY NOT NULL,
  classification_criteria INTEGER NOT NULL,
  application_status application_status_enum,
  datasource_configuration INTEGER NOT NULL,
  error_status TEXT,
  PRIMARY KEY (id, user_id),
  FOREIGN KEY (user_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE,
  FOREIGN KEY (application_dataset) REFERENCES datasets(id),
  FOREIGN KEY (datasource_id) REFERENCES (id),
  FOREIGN KEY (datasource_settings_id) REFERENCES datasource_settings(id)
);
