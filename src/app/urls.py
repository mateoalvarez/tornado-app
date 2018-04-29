"""Webpage urls and handlers"""

from tornado.web import url

from models.home.handlers import HomeHandler
from models.users.handlers import RegisterHandler, LogoutHandler, LoginHandler, UserSettingsHandler
from models.datasets.handlers import DatasetsHandler, DatasetsDeleteHandler
from models.ml_models.handlers import MLModelsHandler
from models.ml_models.aws_deploy_handler import MLModelsAWSDeployHandler
from models.trained_ml_models.handlers import TrainedMLModelsHandler
from models.running_applications.handlers import RunningApplicationsHandler

URL_PATTERNS = [
    # Home
    url(r"/", HomeHandler, name="home"),

    # Auth
    url(r"/auth/register", RegisterHandler, name="register"),
    url(r"/auth/login", LoginHandler, name="login"),
    url(r"/auth/logout", LogoutHandler, name="logout"),

    # datasets
    url(r"/datasets", DatasetsHandler, name="datasets"),
    url(r"/datasets/delete", DatasetsDeleteHandler, name="datasets_delete"),

    # ml_models
    url(r"/ml_models", MLModelsHandler, name="ml_models"),
    url(r"/ml_models/deploy", MLModelsAWSDeployHandler, name="ml_models_deploy"),

    # trained_ml_models
    url(r"/trained_ml_models", TrainedMLModelsHandler, name="trained_ml_models"),
    url(r"/trained_ml_models/deploy", TrainedMLModelsHandler, name="trained_ml_models"),

    # running Applications
    url(r"/running_applications", RunningApplicationsHandler, name="running_applications"),

    # User settings page
    url(r"/user_settings", UserSettingsHandler, name="user_settings"),
]
