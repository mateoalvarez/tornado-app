"""Webpage urls and handlers"""

from tornado.web import url

from models.home.handlers import HomeHandler
from models.users.handlers import RegisterHandler, LogoutHandler, LoginHandler
from models.datasets.handlers import DatasetsHandler
from models.ml_models.handlers import MLModelsHandler
from models.trained_ml_models.handlers import TrainedMLModelsHandler

URL_PATTERNS = [
    # Home
    url(r"/", HomeHandler, name="home"),

    # Auth
    url(r"/auth/register", RegisterHandler, name="register"),
    url(r"/auth/login", LoginHandler, name="login"),
    url(r"/auth/logout", LogoutHandler, name="logout"),

    # datasets
    url(r"/datasets", DatasetsHandler, name="datasets"),

    # ml_models
    url(r"/ml_models", MLModelsHandler, name="ml_models"),

    # trained_ml_models
    url(r"/trained_ml_models", TrainedMLModelsHandler, name="trained_ml_models"),
]
