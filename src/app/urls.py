"""Webpage urls and handlers"""

from tornado.web import url

from models.home.handlers import HomeHandler
from models.users.handlers import RegisterHandler, LogoutHandler, LoginHandler, UserSettingsHandler
from models.applications.handlers import ApplicationsHandler, ApplicationDeletionHandler
from models.applications.handlers import ApplicationDeploymentDeletionHandler, ApplicationDeployer
from models.datasets.handlers import DatasetsHandler, DatasetsDeleteHandler
from models.pipelines.handlers import MLModelsHandler, MLModelsHandlerDelete
from models.pipelines.aws_deploy_handler import MLModelsAWSDeployHandler
from models.running_applications.handlers import RunningApplicationsHandler
from models.running_applications.handlers import VisualizeApplicationsHandler, DownloadDataHandler
from models.datasource_settings.handlers import DataSourceSettingsHandler

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

    # Pipelines
    url(r"/pipelines", MLModelsHandler, name="pipelines"),
    url(r"/pipelines/delete", MLModelsHandlerDelete, name="pipelines_delete"),
    url(r"/pipelines/deploy", MLModelsAWSDeployHandler, name="pipelines_deploy"),

    # Applications
    url(r"/applications", ApplicationsHandler, name="applications"),
    url(r"/applications/deploy", ApplicationDeployer, name="applications_deploy"),
    url(r"/applications/stop", ApplicationDeploymentDeletionHandler, name="applications_stop"),
    url(r"/applications/delete", ApplicationDeletionHandler, name="applications_delete"),

    # running Applications
    url(r"/running_applications", RunningApplicationsHandler, name="running_applications"),
    url(r"/running_applications/visualize", VisualizeApplicationsHandler,
        name="visualize_running_applications"),
    url(r"/running_applications/download", DownloadDataHandler, name="download_processed_data"),

    # User settings page
    url(r"/user_settings", UserSettingsHandler, name="user_settings"),

    # User twitter settings
    url(r"/datasource_settings", DataSourceSettingsHandler, name="datasource_settings")
]
