"""Web site settings"""
import os
import logging.config
import base64
import tornado
import tornado.template
from tornado.options import options, define
from jinja2 import Environment, FileSystemLoader


# Make filepaths relative to settings.
LOCATION = lambda x: os.path.join(
    os.path.dirname(os.path.realpath(__file__)), x)

STATIC_ROOT = LOCATION('static')

# Make filepaths relative to settings.
PATH = lambda root, *a: os.path.join(root, *a)
ROOT = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_ROOT = PATH(ROOT, 'templates')
CERT_ROOT = PATH(ROOT, 'certs')
LOCALE_ROOT = PATH(ROOT, 'translations')
# Deployment configuration

tornado.options.parse_command_line()

# Tornado server configuration
define("port", default=8888, help="Run on the given port", type=int)
define("config", default=None, help="Tornado config file")
define("debug", default=False, help="Debug mode")
define("ssl_options", default={
    "certfile": CERT_ROOT + '/cert.pem',
    "keyfile": CERT_ROOT + '/key.pem'
})
define("locale_dir", default=LOCALE_ROOT, help='Locale template directory')
define("default_locale", default='es_ES', help="Default locale")

COOKIE_SECRET = base64.b64encode(os.urandom(50)).decode('ascii')

settings = {
    'debug': options.debug,
    'static_path': STATIC_ROOT,
    'cookie_secret': COOKIE_SECRET,
    'cookie_expires': 31,
    'xsrf_cookies': False,
    'login_url': '/auth/login',
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
            'filename': LOCATION('logs/main.log'),
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
