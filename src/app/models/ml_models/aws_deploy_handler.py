"""Complementary handler for aws interaction"""

import requests
import json
from ..base.handlers import BaseHandler
from .job_builder import JobAssemblerHandler

class MLModelsAWSDeployHandler(BaseHandler):
    """Handler to deploy jobs on AWS"""

    @staticmethod
    def _create_job_json_from_template(elements_to_replace):
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

    def _create_application_job_file(self, application):
        """Generate spark job code"""

        return

    def _upload_emr_files(self, spark_job_file, prereq_file, application_id):
        """UPLOAD files and return url"""

        prereq_file_url = "{user}/{application_id}/prerequisites_{application_id}.sh".\
            format(user=self.current_user["email"], application_id=application_id)
        spark_job_file_url = "{user}/{application_id}/spark_job_{application_id}".\
            format(user=self.current_user["email"], application_id=application_id)

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

    def _deploy_emr_application_training(self, application, spark_job_file_url, prereq_file_url):
        """DEPLOT application on cluster"""

        elements_to_replace = {
            "user": self.current_user["email"],
            "spark-job": spark_job_file_url,
            "application_id": application["id"],
            "preconfig_script": prereq_file_url
        }

        job_step_content = self._create_job_json_from_template(elements_to_replace=elements_to_replace)

        emr_client = self.start_emr_connection()
        result = emr_client.run_job_flow(**job_step_content)
        print("\n\n\n\n\n\n\n", result, "\n\n\n\n\n")


    def get(self):
        """GET application deployment information"""

    def post(self):
        """CREATE deployment on AWS"""

        application_id = self.get_argument("application", "")
        self.db_cur.execute\
        (\
            "SELECT * FROM applications WHERE id=%s;",\
            (application_id,)
        )
        application = self.db_cur.fetchone()
        print(application)

        # spark_job_file, prereq_file = self._create_emr_files(application)

        spark_job_file_url, prereq_file_url = self._upload_emr_files(spark_job_file, prereq_file, application_id)

        # self._deploy_emr_application_training(application, spark_job_file_url, prereq_file_url)

        self.redirect(self.get_argument("next", "/ml_models"))
