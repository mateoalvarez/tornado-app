"""Home page handlers"""
import logging
import tornado
import json
from tornado import gen
from ..base.handlers import BaseHandler
from .dispatcher_deployer import DispatcherDeployer

LOGGER = logging.getLogger(__name__)

class TrainedMLModelsHandler(BaseHandler):
    """ Home page handler """

    def _get_k8s_config():
        """Retrieve configuration for k8s"""

    def _parse_application_configuration(datasource_configuration):
        """Parse information from application configuration"""
        datasource_configuration_dict = json.loads(datasource_configuration)
        return datasource_configuration_dict

    @gen.coroutine
    @tornado.web.authenticated
    def get(self):
        "GET method on trained models page"
        self.db_cur.execute("SELECT * FROM applications WHERE user_id=%s;", (self.current_user["id"], ))
        user_applications = self.db_cur.fetchall()
        self.render("trained_ml_models/trained_ml_models.html",\
                     user_applications=user_applications
                   )
    @gen.coroutine
    @tornado.web.authenticated
    def post(self):
        "Create application and start running"

        application_id = self.get_argument("application_id", None)
        self.db_cur.execute("SELECT * FROM applications WHERE id=%s;", (application_id, ))
        application = self.db_cur.fetchone()

        # Create datasource_configurations
        # self.db_cur.execute("SELECT * FROM datasource_settings WHERE user_id=%s;", (self.current_user["id"], ))
        # datasource_settings = self.db_cur.fetchone()
        datasource_settings_id = self.get_argument("datasource_settings_id", None)
        if datasource_settings_id is None:
            # if datasource settings is not set, select default application configuration
            self.db_cur.execute("SELECT * FROM datasource_settings WHERE user_id=%s;", (1, ))
            datasource_settings_id = self.db_cur.fetchone()["id"]
            self.db_cur.execute("UPDATE applications SET datasource_settings_id=(%s) WHERE id=(%s);", (datasource_settings_id, application_id, ))
            self.db_conn.commit()

        datasource_keywords = str(self.get_argument("keywords", "big data, ai"))

        print('\n\n\n')
        print(datasource_settings_id)
        print('\n\n\n')

        self.db_cur.execute("INSERT INTO datasource_configurations (datasource_settings_id, datasource_application_config) VALUES (%s, %s) returning id;", (datasource_settings_id, '{"keywords":"' + datasource_keywords + '"}', ))
        datasource_configuration_id = self.db_cur.fetchone()["id"]
        self.db_conn.commit()

        # Update application configuration
        self.db_cur.execute("UPDATE applications SET datasource_configuration_id=(%s) WHERE id=(%s);", (datasource_configuration_id, application_id, ))

        dispatcher_deployer = DispatcherDeployer(\
        k8s_config=self.k8s_config,\
        k8s_namespace=self.k8s_namespace,\
        BUCKET_YAML_TEMPLATES=self.BUCKET_YAML_TEMPLATES,\
        BUCKET_YAML_TEMPLATES_REGION=self.BUCKET_YAML_TEMPLATES_REGION\
        )

        application_datasource_configuration = ""
        dispatcher_deployer.deploy_dispatcher(application["id"], self.current_user["id"], application_datasource_configuration)
        dispatcher_deployer.deploy_kafka_producer(application["id"], datasource_keywords)
        dispatcher_deployer.deploy_models(application)
        dispatcher_deployer.deploy_preprocessing(application)

        self.redirect(self.get_argument("next", "/trained_ml_models"))
