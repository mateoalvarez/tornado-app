"""Home page handlers"""
import logging
import tornado
from tornado import gen
import json
from ..base.handlers import BaseHandler

LOGGER = logging.getLogger(__name__)

class MLModelsHandler(BaseHandler):
    """ Home page handler """
# Aux functions

    def _get_data_prep_methods(self):
        """GET preprocessing methods"""
        self.db_cur.execute\
        (\
            "SELECT * FROM preprocessing_methods;"\
        )
        data_prep_methods = self.db_cur.fetchall()
        return data_prep_methods

    def _get_user_pipelines(self):
        """GET user's pipelines"""
        self.db_cur.execute\
        (\
            "SELECT * FROM pipelines WHERE user_id=%s;", (self.current_user["id"],)\
        )
        pipelines = self.db_cur.fetchall()
        return pipelines

    def _get_models(self):
        """GET models"""
        self.db_cur.execute\
        (\
            "SELECT * FROM models;"
        )
        models = self.db_cur.fetchall()
        return models

    def _get_datasets(self):
        """GET all datasets from user and public"""
        self.db_cur.execute\
        (\
            "SELECT * FROM datasets;"
        )
        datasets = self.db_cur.fetchall()
        return datasets

    def _get_classification_criteria(self):
        """GET classification_criteria"""
        self.db_cur.execute\
        (\
            "SELECT * FROM classification_criteria;"
        )
        classification_criteria = self.db_cur.fetchall()
        return classification_criteria
# Handler methods

    @gen.coroutine
    @tornado.web.authenticated
    def get(self):
        """GET method on dataset page"""

        data_prep_methods = self._get_data_prep_methods()
        models = self._get_models()
        user_pipelines = self._get_user_pipelines()
        datasets = self._get_datasets()
        classification_criteria = self._get_classification_criteria()

        self.render\
        (\
            "ml_models/ml_models.html",\
            datasets=datasets,\
            data_prep_methods=data_prep_methods,\
            user_pipelines=user_pipelines,\
            models=models,\
            classification_criteria=classification_criteria
        )

    @gen.coroutine
    @tornado.web.authenticated
    def post(self):
        """CREATE and deploy training works"""

        self.db_cur.execute\
        (\
            "INSERT INTO pipelines (user_id, pipeline_name, pipeline_engine, pipeline_dataset,\
            pipeline_prep_stages, pipeline_models, classification_criteria, training_status\
             ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);",\
             (\
                 self.current_user["id"],\
                 self.get_argument("pipeline_name", ""),\
                 self.get_argument("pipeline_engine", "1"),\
                 self.get_argument("pipeline_dataset", ""),\
                 self.get_argument("pipeline_prep_stages", ""),\
                 self.get_argument("pipeline_models", ""),\
                 self.get_argument("classification_criteria", ""),\
                 self.get_argument("training_status", "1")\
             )
        )
        self.db_conn.commit()

        self.redirect(self.get_argument("next", "/ml_models"))


class MLModelsAWSDeployHandler(BaseHandler):
    """Handler to deploy jobs on AWS"""

    def _create_job_from_template(self, params):
        """Create configuration from template and params"""

        template = json.loads("emr_basic_template.json")


    def _upload_EMR_job_to_S3(self, file_content, pipeline):
        """Upload job file to S3 and return url"""

        filename = "spark_job" + pipeline

        s3_client, s3_resource = self.start_AWS_connection("s3")

        s3_client.put_object\
        (\
            Bucket=self.BUCKET_SPARK_JOBS,\
            Body=file_content,\
            Key=self.current_user["email"] + "/" + filename
        )

    def _deploy_EMR_pipeline_training(self):
        """DEPLOT pipeline on cluster"""

    def post(self):
        """CREATE deployment on AWS"""
        pipeline_id = self.get_argument("pipeline", "")
        self.db_cur.execute\
        (\
            "SELECT * FROM pipelines WHERE id=%s;",\
            (pipeline_id,)
        )
        pipeline = self.db_cur.fetchone()
        print("##############\n\n\n deploy")
# TODO deploy on emr
        self.redirect(self.get_argument("next", "/ml_models"))
