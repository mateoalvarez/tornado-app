"""Home page handlers"""
import logging
import tornado
from tornado import gen
from ..base.handlers import BaseHandler
from .dispatcher_deployer import DispatcherDeployer

LOGGER = logging.getLogger(__name__)

class TrainedMLModelsHandler(BaseHandler):
    """ Home page handler """

    def _get_k8s_config():
        """Retrieve configuration for k8s"""

    @gen.coroutine
    @tornado.web.authenticated
    def get(self):
        "GET method on trained models page"
        self.db_cur.execute("SELECT * FROM applications WHERE user_id=%s;", (self.current_user["id"], ))
        user_applications = self.db_cur.fetchall()
        self.render("trained_ml_models/trained_ml_models.html",\
                     user_applications=user_applications
                   )

    def post(self):
        "Create application and start running"

        application_id = self.get_argument("application", "")
        self.db_cur.execute("SELECT * FROM applications WHERE id=%s;", (application_id, ))
        application = self.db_cur.fetchone()
        dispatcher_deployer = DispatcherDeployer(\
        k8s_config=self.k8s_config,\
        k8s_namespace=self.k8s_namespace,\
        BUCKET_YAML_TEMPLATES=self.BUCKET_YAML_TEMPLATES,\
        BUCKET_YAML_TEMPLATES_REGION=self.BUCKET_YAML_TEMPLATES_REGION
        )
        dispatcher_deployer.deploy_dispatcher(application)
        dispatcher_deployer.deploy_kafka_producer(application)

        self.redirect(self.get_argument("next", "/trained_ml_models"))
