"""Complementary handler for aws interaction"""

import requests
import json
from ..base.handlers import BaseHandler
from .spark_job_builder import SparkJobAssemblerHandler

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

    def _create_spark_job_file(self, pipeline):
        """Generate spark job code"""

        pipeline_stages = [pipeline.pipeline_prep_stages, pipeline.pipeline_models]
        spark_job_file = ""

        for pipeline_stage in pipeline_stages:

            spark_job_file += self._get_spark_code_block(pipeline_stage).code_content + "\n"

        #  TODO create file from options MODULABLE
        # spark_job_file =\
        #     '''
        #         import pyspark
        #         sc = pyspark.SparkContext()
        #         data = [1, 2, 3, 4, 5]
        #         distData = sc.parallelize(data)
        #         sc.saveAsTextFile("s3://tornado-app-emr/mateyo@msn.com/1/log/file")
        #     '''
        return spark_job_file

    def _create_emr_files(self, pipeline):
        """CREATE spark job and prerequisites files"""

        # prerequisites file
        prereq_file = self._create_prerequisites_from_template()
        # spark job file
        # spark_job_file = SparkJobAssemblerHandler.spark_job_assembler(pipeline)
        spark_job_file = self._create_spark_job_file(pipeline)

        return spark_job_file, prereq_file

    def _upload_emr_files(self, spark_job_file, prereq_file, job_id):
        """UPLOAD files and return url"""

        prereq_file_url = "{user}/{job_id}/prerequisites_{job_id}.sh".\
            format(user=self.current_user["email"], job_id=job_id)
        spark_job_file_url = "{user}/{job_id}/spark_job_{job_id}".\
            format(user=self.current_user["email"], job_id=job_id)

        s3_client, _ = self.start_s3_connection()

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
        # prereq_file_url = "s3://tornado-app-emr/" + prereq_file_url
        prereq_file_url = 's3://tornado-app-emr/Templates/prereq_template.sh'

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
        print(pipeline)

        spark_job_file, prereq_file = self._create_emr_files(pipeline)

        spark_job_file_url, prereq_file_url = self._upload_emr_files(\
            spark_job_file, prereq_file, pipeline["id"])

        self._deploy_emr_pipeline_training(pipeline, spark_job_file_url, prereq_file_url)

        self.redirect(self.get_argument("next", "/ml_models"))
