import os
import logging.config
import tornado
import tornado.template
from tornado.options import options, define
from jinja2 import Environment, FileSystemLoader

import base64
import uuid

# Make filepaths relative to settings.
location = lambda x: os.path.join(
    os.path.dirname(os.path.realpath(__file__)), x)

# Tornado server configuration
define("port", default=8888, help="Run on the given port", type=int)
define("config", default=None, help="Tornado config file")
define("debug", default=False, help="Debug mode")

tornado.options.parse_command_line()

STATIC_ROOT = location('static')
# TEMPLATE_ROOT = location('templates')
# TEMPLATE_ROOT = location("/Users/Mat/github/tornado-app/src/app/templates")

# Make filepaths relative to settings.
path = lambda root,*a: os.path.join(root, *a)
ROOT = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_ROOT = path(ROOT, 'templates')
# Deployment configuration

cookie_secret = base64.b64encode(os.urandom(50)).decode('ascii')

settings = {
    'debug': options.debug,
    'static_path': STATIC_ROOT,
    'cookie_secret': cookie_secret,
    'cookie_expires': 31,
    'xsrf_cookies': True,
    'login_url': '/login/',
    'template_loader': tornado.template.Loader(TEMPLATE_ROOT),
}

# Jinja settings

jinja_settings = {
    'autoescape': True,
    'extensions': [
        'jinja2.ext.with_'
    ],
}

jinja_env = Environment(loader = FileSystemLoader(TEMPLATE_ROOT), **jinja_settings)

# PSQL Settings

PSQL_DB = {
    'host': 'localhost',
    'port': 32768,
    'db_name': 'twitter_app_db',
    'reconnect_tries': 5,
    'reconnect_timeout': 2, #Seconds
}




# See PEP 391 and logconfig for formatting help.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'main_formatter': {
            'format': '%(levelname)s:%(name)s: %(message)s '
            '(%(asctime)s; %(filename)s:%(lineno)d)',
            'datefmt': "%Y-%m-%d %H:%M:%S",
        },
    },
    'handlers': {
        'rotate_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': location('logs/main.log'),
            'when': 'midnight',
            'interval':    1,  # day
            'backupCount': 7,
            'formatter': 'main_formatter',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'main_formatter',
            # 'filters': ['require_local_true'],
        },
    },
    'loggers': {
        '': {
            'handlers': ['rotate_file', 'console'],
            'level': 'DEBUG',
        }
    }
}

logging.config.dictConfig(LOGGING)

if options.config:
    tornado.options.parse_config_file(options.config)
