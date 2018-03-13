"""Schemas of models"""
USERS = {
    "id": "id  SERIAL PRIMARY KEY",
    "email": "email VARCHAR",
    "password": "password VARCHAR",
    "name": "name CHARACTER [20]",
    "type": "type INTEGER NOT NULL",
    "PRIMARY KEY": "PRIMARY KEY (id)",
}

TWITTER_ACCOUNTS = {
    "id": "id SERIAL PRIMARY KEY",
    "user_id": "user_id INTEGER NOT NULL",
    "tokens": "tokens VARCHAR",
    "twitter_apps": "twitter_apps VARCHAR",
    "PRIMARY KEY": "PRIMARY KEY (id, user_id)",
    "FOREIGN KEY": "FOREIGN KEY (user_id) REFERENCES users (id) \
    ON UPDATE CASCADE ON DELETE CASCADE",
}

ML_MODELS = {
    "id": ["id SERIAL PRIMARY KEY"],
    "display_name": ["display_name VARCHAR"],
    "type": ["type INTEGER"],
    "PRIMARY KEY": ["PRIMARY KEY id"],
}

TRAINED_MODELS = {
    "id": "id SERIAL PRIMARY KEY",
    "user_id": "user_id INTEGER NOT NULL",
    "ml_model_id": "ml_model_id INTEGER NOT NULL",
    "display_name": "display_name CHARACTER [15]",
    "metrics": "metrics JSONB",
    "configuration": "configuration JSONB",
    "PRIMARY KEY": "PRIMARY KEY (id, user_id, ml_model_id)",
    "FOREIGN KEY":
        "FOREIGN KEY (user_id) REFERENCES users (id) ON UPDATE CASCADE ON DELETE CASCADE,\
        FOREIGN KEY (ml_model_id) REFERENCES ml_models ON UPDATE CASCADE ON DELETE CASCADE"
}

DATASETS = {
    "id": "id SERIAL PRIMARY KEY",
    "user_id": "user_id INTEGER NOT NULL",
    "store_url": "store_url VARCHAR NOT NULL",
    "statistics": "statistics JSONB",
    "PRIMARY KEY": "PRIMARY KEY (id, user_id)",
    "FOREIGN KEY": "FOREIGN KEY (user_id) REFERENCES users (id) ON UPDATE CASCADE ON DELETE CASCADE"
}

CLASSIFIERS = {
    "id": "id SERIAL PRIMARY KEY",
    "model_ids": "model_ids JSONB",
}

RUNNING_APPLICATIONS = {
    "id": "id SERIAL PRIMARY KEY",
    "user_id": "user_id INTEGER NOT NULL",
    "PRIMARY KEY": "PRIMARY KEY (id)",
    "FOREIGN KEY": "FOREIGN KEY (user_id) REFERENCES users (id) ON UPDATE CASCADE ON DELETE CASCADE"
}
