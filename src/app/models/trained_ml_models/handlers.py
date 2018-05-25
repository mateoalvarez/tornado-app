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
    #
    # def _get_k8s_config():
    #     """Retrieve configuration for k8s"""

    def _parse_application_configuration(self, datasource_configuration):
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

        datasource_settings_id = self.get_argument("datasource_settings_id", None)

        if datasource_settings_id == "None":
            # if datasource settings is not set, select default application configuration
            self.db_cur.execute("SELECT * FROM datasource_settings WHERE user_id=%s;", (1, ))
            datasource_settings_id = self.db_cur.fetchone()["id"]
            self.db_cur.execute("UPDATE applications SET datasource_settings_id=(%s) WHERE id=(%s);", (datasource_settings_id, application_id, ))
            self.db_conn.commit()

        datasource_keywords = str(self.get_argument("keywords", "big data, ai"))

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

        application_datasource_configuration = '\{"code":"codigo"\}'
        classification_configuration = '\{"code":"codigo"\}'
        S3_CLIENT, S3_RESOURCE =  self.start_s3_connection()
        try:
            model_urls = ['https://s3.eu-central-1.amazonaws.com/tornado-app-emr/'+element["Key"] for element in S3_CLIENT.list_objects_v2(\
            Bucket=self.BUCKET_SPARK_JOBS,\
            Prefix='user_{user_id}/models/application_{application_id}'.format(user_id=self.current_user["id"], application_id=application_id),\
            StartAfter='user_{user_id}/models/application_{application_id}'.format(user_id=self.current_user["id"], application_id=application_id))["Contents"]]

            # print('\n\n\n\n\n\n')
            # print('######################')
            # print(model_urls)
            # print('######################')
            # print('\n\n\n\n\n\n')

            preprocessing_url = 'https://s3.eu-central-1.amazonaws.com/tornado-app-emr/user_{user_id}/models/application_{application_id}/preprocessing.zip'.format(user_id=self.current_user["id"], application_id=application_id)

# SET PUBLIC PERMISSIONS TO FILES
            # print("#############################")
            # print("#############################")
            # print(preprocessing_url.replace('https://s3.' + self.BUCKET_SPARK_JOBS_REGION + '.amazonaws.com/' + self.BUCKET_SPARK_JOBS + '/', ''))
            # print("#############################")
            # print("#############################")
            preprocessing_acl = S3_RESOURCE.ObjectAcl(self.BUCKET_SPARK_JOBS, preprocessing_url.replace('https://s3.' + self.BUCKET_SPARK_JOBS_REGION + '.amazonaws.com/' + self.BUCKET_SPARK_JOBS + '/', ''))
            response = preprocessing_acl.put(ACL='public-read')
            for model_url in model_urls:
                model_acl = S3_RESOURCE.ObjectAcl(self.BUCKET_SPARK_JOBS, model_url.replace('https://s3.' + self.BUCKET_SPARK_JOBS_REGION + '.amazonaws.com/' + self.BUCKET_SPARK_JOBS + '/', ''))
                response = model_acl.put(ACL='public-read')

            model_urls.remove(preprocessing_url)

            dispatcher_deployer.deploy_models(\
                application_id=application["id"],\
                model_ids=application["application_models_ids"],\
                model_urls=model_urls)

            dispatcher_deployer.deploy_preprocessing(\
                application_id=application["id"],\
                preprocessing_ids=application["application_prep_stages_ids"],\
                preprocessing_url=preprocessing_url)

            dispatcher_deployer.deploy_dispatcher(\
            **application,\
            datasource_configuration=application_datasource_configuration,\
            classification_configuration=classification_configuration\
            )
            dispatcher_deployer.deploy_kafka_producer(\
                application_id=application["id"],\
                keywords=datasource_keywords)

            # Update application status -> to 'running'
            self.db_cur.execute("UPDATE applications SET application_status='running' WHERE id=(%s);", (application_id,))
            self.db_conn.commit()

            self.redirect(self.get_argument("next", "/trained_ml_models"))
        except Exception as exception:
            print('######## ERROR ########')
            print(exception)
            print('######## ERROR ########')
            self.redirect(self.get_argument("next", "/trained_ml_models"))


class ApplicationDeletionHandler(BaseHandler):
    """Handler to delete applications deployment"""

    @gen.coroutine
    @tornado.web.authenticated
    def post(self):
        """Delete method to destroy apps"""

        application_id = self.get_argument("application_id", None)
        self.db_cur.execute("SELECT * FROM applications WHERE id=%s;", (application_id, ))
        application = self.db_cur.fetchone()

        self.db_cur.execute("UPDATE FROM applications SET application_status='stopped' WHERE id=%s", (application["id"], ))

        dispatcher_deployer = DispatcherDeployer(\
        k8s_config=self.k8s_config,\
        k8s_namespace=self.k8s_namespace,\
        BUCKET_YAML_TEMPLATES=self.BUCKET_YAML_TEMPLATES,\
        BUCKET_YAML_TEMPLATES_REGION=self.BUCKET_YAML_TEMPLATES_REGION\
        )
