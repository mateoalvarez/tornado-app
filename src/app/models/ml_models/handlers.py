"""Home page handlers"""
import logging
import tornado
from tornado import gen
import json
import requests
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

    @staticmethod
    def _create_job_from_template(elements_to_replace):
        """Create configuration from template and params"""

        json_template_file = requests.get(\
        "https://s3.eu-central-1.amazonaws.com/tornado-app-emr/Templates/emr_basic_template.json")\
        .content.decode("utf-8")
        # REPLACE VALUES
        json_template_filled = json_template_file
        for element_to_replace_key, element_to_replace_value in\
         zip(list(elements_to_replace.keys()), list(elements_to_replace.values())):
            json_template_filled = json_template_filled.replace\
            ("{" + element_to_replace_key + "}", str(element_to_replace_value))

        template = json.loads(json_template_filled)
        import pprint
        pprint.pprint(template)
        return template

    @staticmethod
    def _create_prerequisites_from_template():
        """GET template for prereq"""

        prereq_file = requests.get(\
        "https://s3.eu-central-1.amazonaws.com/tornado-app-emr/Templates/prereq_template.sh")\
        .content

        return prereq_file

    @staticmethod
    def _create_spark_job_file(pipeline):
        """Generate spark job code"""
        #  TODO create file from options MODULABLE
        spark_job_file =\
            '''
                import pyspark
                sc = pyspark.SparkContext()
                data = [1, 2, 3, 4, 5]
                distData = sc.parallelize(data)
                sc.saveAsTextFile("s3://tornado-app-emr/mateyo@msn.com/1/log/file")
            '''
        return spark_job_file

    def _create_emr_files(self, pipeline):
        """CREATE spark job and prerequisites files"""

        # prerequisites file
        prereq_file = self._create_prerequisites_from_template()
        # spark job file
        spark_job_file = self._create_spark_job_file(pipeline)

        return spark_job_file, prereq_file

    def _upload_emr_files(self, spark_job_file, prereq_file, job_id):
        """UPLOAD files and return url"""

        prereq_file_url = "{user}/{job_id}/prerequisites_{job_id}.sh".\
            format(user=self.current_user["email"], job_id=job_id)
        spark_job_file_url = "{user}/{job_id}/spark_job_{job_id}".\
            format(user=self.current_user["email"], job_id=job_id)

        s3_client, _ = self.start_AWS_connection("s3")

        s3_client.put_object\
        (\
            ACL="public-read-write",\
            Bucket=self.BUCKET_SPARK_JOBS,\
            Body=spark_job_file,\
            Key=spark_job_file_url
        )

        s3_client.put_object\
        (\
            ACL="public-read-write",\
            Bucket=self.BUCKET_SPARK_JOBS,\
            Body=prereq_file,\
            Key=prereq_file_url
        )
        spark_job_file_url = "s3://tornado-app-emr/" + spark_job_file_url
        prereq_file_url = "s3://tornado-app-emr/" + prereq_file_url
        # prereq_file_url = "s3://tornado-app-emr/" + prereq_file_url

        return spark_job_file_url, prereq_file_url

    def _deploy_emr_pipeline_training(self, pipeline, spark_job_file_url, prereq_file_url):
        """DEPLOT pipeline on cluster"""

        elements_to_replace = {
            "user": self.current_user["email"],
            "spark-job": spark_job_file_url,
            "job_id": pipeline["id"],
            "preconfig_script": prereq_file_url
        }

        job_step_content = self._create_job_from_template(elements_to_replace=elements_to_replace)

        emr_client = self.start_emr_connection()
        result = emr_client.run_job_flow(**job_step_content)
        print("\n\n\n\n\n\n\n", result, "\n\n\n\n\n")


    def get(self):
        """GET pipeline deployment information"""

    def post(self):
        """CREATE deployment on AWS"""

        pipeline_id = self.get_argument("pipeline", "")
        self.db_cur.execute\
        (\
            "SELECT * FROM pipelines WHERE id=%s;",\
            (pipeline_id,)
        )
        pipeline = self.db_cur.fetchone()

        spark_job_file, prereq_file = self._create_emr_files(pipeline)

        spark_job_file_url, prereq_file_url = self._upload_emr_files(\
            spark_job_file, prereq_file, pipeline["id"])

        self._deploy_emr_pipeline_training(pipeline, spark_job_file_url, prereq_file_url)

        self.redirect(self.get_argument("next", "/ml_models"))
