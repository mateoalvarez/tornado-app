"""Home page handlers"""
import logging
import tornado
import json
from tornado import gen
from ..base.handlers import BaseHandler
from .dispatcher_deployer import DispatcherDeployer

LOGGER = logging.getLogger(__name__)


class ApplicationsHandler(BaseHandler):
    """ Home page handler """

    def _parse_application_configuration(self, datasource_configuration):
        """Parse information from application configuration"""
        datasource_configuration_dict = json.loads(datasource_configuration)
        return datasource_configuration_dict

    @gen.coroutine
    @tornado.web.authenticated
    def get(self):
        "GET method on trained models page"
        self.db_cur.execute(
            "SELECT * FROM applications WHERE user_id=%s;",
            (self.current_user["id"], )
        )
        user_applications = self.db_cur.fetchall()
        self.db_cur.execute(
            "SELECT * FROM pipelines WHERE user_id=%s;",
            (self.current_user["id"], )
        )
        user_pipelines = self.db_cur.fetchall()
        self.db_cur.execute(
            "SELECT * FROM pipelines WHERE user_id=1;"
        )
        public_pipelines = self.db_cur.fetchall()

        self.render("applications/applications.html",
                    user_applications=user_applications,
                    user_pipelines=user_pipelines,
                    public_pipelines=public_pipelines
                    )

    @gen.coroutine
    @tornado.web.authenticated
    def post(self):
        "Create application"

        datasource_settings_id = self.get_argument("datasource_settings_id",
                                                   None, False)
        if datasource_settings_id is None or datasource_settings_id == "None":
            # default application configuration
            self.db_cur.execute(
                "SELECT id FROM datasource_settings WHERE user_id=%s;", (1, ))

            datasource_settings_id = self.db_cur.fetchone()["id"]

        datasource_keywords = str(
            self.get_argument("keywords", "big data, ai", True)).replace(" ", "")

        self.db_cur.execute(
            "INSERT INTO datasource_configurations \
            (datasource_settings_id, datasource_application_config)\
            VALUES (%s, %s) returning id;", (
                datasource_settings_id,
                '{"keywords":"' + datasource_keywords + '"}', )
            )
        datasource_configuration_id = self.db_cur.fetchone()["id"]
        self.db_conn.commit()

        application_pipeline = self.get_argument("pipeline_id", "")
        application_name = self.get_argument("application_name", "")
        # Create application
        self.db_cur.execute(
            "INSERT INTO applications(application_pipeline, application_name, \
            application_status, datasource_configuration_id,\
            datasource_settings_id, user_id) VALUES (%s, %s, %s, %s, %s, %s);",
            (application_pipeline, application_name, "stopped",
             datasource_configuration_id, datasource_settings_id,
             str(self.current_user["id"]))
        )
        self.db_conn.commit()
        self.redirect(self.get_argument("next", "/applications"))


class ApplicationDeletionHandler(BaseHandler):
    """Handler to deploy applications"""
    @gen.coroutine
    @tornado.web.authenticated
    def post(self):
        "Delete application"
        application_id = self.get_argument("application_id", "", True)
        self.db_cur.execute(
            "DELETE FROM applications WHERE id=%s;", (application_id, )
        )
        self.db_conn.commit()
        self.redirect(self.get_argument("next", "/applications"))


class ApplicationDeployer(BaseHandler):
    """Handler to deploy created applications"""

    @gen.coroutine
    @tornado.web.authenticated
    def post(self):
        "Deploy application"

        dispatcher_deployer = DispatcherDeployer(
            k8s_config=self.k8s_config,
            k8s_namespace=self.k8s_namespace,
            BUCKET_YAML_TEMPLATES=self.BUCKET_YAML_TEMPLATES,
            BUCKET_YAML_TEMPLATES_REGION=self.BUCKET_YAML_TEMPLATES_REGION
        )

        application_datasource_configuration = '\{"code":"codigo"\}'
        classification_configuration = '\{"code":"codigo"\}'
        S3_CLIENT, S3_RESOURCE = self.start_s3_connection()

        application_id = self.get_argument("application_id", "", False)
        pipeline_id = self.get_argument("pipeline_id", "", False)

        datasource_configuration_id = self.get_argument(
            "datasource_configuration_id", "", False)
        self.db_cur.execute(
            "SELECT datasource_application_config FROM datasource_configurations WHERE id=%s",
            (datasource_configuration_id, )
        )
        datasource_keywords = self.db_cur.fetchall()[0]["datasource_application_config"]["keywords"]

        self.db_cur.execute(
            "SELECT * FROM pipelines WHERE id=%s;", (pipeline_id, )
        )
        pipeline = self.db_cur.fetchall()[0]

        try:
            model_urls = [
                'https://s3.eu-central-1.amazonaws.com/tornado-app-emr/'
                + element["Key"] for element in S3_CLIENT.list_objects_v2(
                    Bucket=self.BUCKET_SPARK_JOBS,
                    Prefix='user_{user_id}/models/pipeline_{pipeline_id}'
                    .format(
                        user_id=self.current_user["id"],
                        pipeline_id=pipeline_id),
                    StartAfter='user_{user_id}/models/pipeline_{pipeline_id}'
                    .format(
                        user_id=self.current_user["id"],
                        pipeline_id=pipeline_id))["Contents"]]

            preprocessing_url = 'https://s3.eu-central-1.amazonaws.com/tornado-app-emr/user_{user_id}/models/pipeline_{pipeline_id}/preprocessing.zip'.format(
                user_id=self.current_user["id"],
                pipeline_id=pipeline_id)

# SET PUBLIC PERMISSIONS TO FILES

            preprocessing_acl = S3_RESOURCE.ObjectAcl(
                self.BUCKET_SPARK_JOBS,
                preprocessing_url.replace('https://s3.'
                                          + self.BUCKET_SPARK_JOBS_REGION
                                          + '.amazonaws.com/'
                                          + self.BUCKET_SPARK_JOBS + '/', ''))
            print('\n\n\n\n')
            print(preprocessing_acl)
            preprocessing_acl.put(ACL='public-read')

            for model_url in model_urls:
                model_acl = S3_RESOURCE.ObjectAcl(
                    self.BUCKET_SPARK_JOBS,
                    model_url.replace(
                        'https://s3.'
                        + self.BUCKET_SPARK_JOBS_REGION
                        + '.amazonaws.com/'
                        + self.BUCKET_SPARK_JOBS + '/', ''))
                model_acl.put(ACL='public-read')

            model_urls.remove(preprocessing_url)

            print("\n\n\n\n")
            print("DEPLOY MODELS")
            print("\n\n\n\n")

            dispatcher_deployer.deploy_models(
                pipeline_id=pipeline_id,
                model_ids=pipeline["pipeline_models_ids"],
                model_urls=model_urls)

            dispatcher_deployer.deploy_preprocessing(
                pipeline_id=pipeline_id,
                preprocessing_ids=pipeline["pipeline_prep_stages_ids"],
                preprocessing_url=preprocessing_url)

            dispatcher_deployer.deploy_dispatcher(
                **pipeline,
                application_id=application_id,
                datasource_configuration=application_datasource_configuration,
                classification_configuration=classification_configuration
            )
            dispatcher_deployer.deploy_kafka_producer(
                application_id=application_id,
                keywords=datasource_keywords
                )

            # Update application status -> to 'running'
            self.db_cur.execute(
                "UPDATE applications SET application_status='running' WHERE id=(%s);",
                (application_id,))
            self.db_conn.commit()

            self.redirect(self.get_argument("next", "/applications"))

        except Exception as exception:
            print('######## ERROR ########')
            print(exception)
            print('######## ERROR ########')
            self.redirect(self.get_argument("next", "/applications"))


class ApplicationDeploymentDeletionHandler(BaseHandler):
    """Handler to delete applications deployment"""

    @gen.coroutine
    @tornado.web.authenticated
    def post(self):
        """Delete method to destroy apps"""

        application_id = self.get_argument("application_id", None)
        self.db_cur.execute(
            "SELECT * FROM applications WHERE id=%s;", (application_id, )
            )
        application = self.db_cur.fetchone()

        self.db_cur.execute(
            "SELECT * FROM pipelines WHERE id=%s;",
            (application["application_pipeline"], )
        )
        pipeline = self.db_cur.fetchall()[0]

        dispatcher_deployer = DispatcherDeployer(
            k8s_config=self.k8s_config,
            k8s_namespace=self.k8s_namespace,
            BUCKET_YAML_TEMPLATES=self.BUCKET_YAML_TEMPLATES,
            BUCKET_YAML_TEMPLATES_REGION=self.BUCKET_YAML_TEMPLATES_REGION
            )
        dispatcher_deployer.delete_deployments(
            application_id=application_id,
            pipeline_id=pipeline["id"],
            preprocessing_ids=pipeline["pipeline_prep_stages_ids"],
            model_ids=pipeline["pipeline_models_ids"]
            )

        self.db_cur.execute(
            "UPDATE applications SET application_status='stopped' WHERE id=%s;",
            (application["id"], )
            )
        self.db_conn.commit()
        self.redirect(self.get_argument("next", "/applications"))
