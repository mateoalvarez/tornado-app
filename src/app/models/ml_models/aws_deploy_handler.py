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

        for element_to_replace_key, element_to_replace_value in elements_to_replace.items():
            json_template_filled = json_template_filled.replace\
            ("{" + element_to_replace_key + "}", str(element_to_replace_value))
        # print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
        # print(json_template_filled)
        # print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
        template = json.loads(json_template_filled)
        from pprint import pprint
        print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
        pprint(template)
        print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
        return template

    @staticmethod
    def _create_prerequisites_from_template(job_file_url):
        """GET template for prereq"""

        # print('\n\n\n\n')
        # print('#######################')
        # print(job_file_url)
        # print('\n\n\n\n')

        prereq_file = requests.get(\
        "https://s3.eu-central-1.amazonaws.com/tornado-app-emr/Templates/prereq_template_job_file.sh")\
        .content.decode('utf-8').format(job_file=job_file_url)

        return prereq_file

    def _create_application_job_file(self, application):
        """Generate spark job code"""
        stages = application['application_prep_stages_ids'] + application['application_models_ids']
        # Create code execution
        # stages = ['input', 'preprocessing', 'model', 'output']
        full_job_file = ''
        # Initializer
        self.db_cur.execute('SELECT storage_url FROM datasets WHERE id=%s', (application['application_dataset'], ))
        dataset = self.db_cur.fetchone()['storage_url']

        self.db_cur.execute('SELECT * FROM code_block_templates WHERE template_name=%s;', ('initializer', ))
        initializer = self.db_cur.fetchone()['code_content']
        full_job_file = initializer['code'].replace("<dataset>", dataset)

        for stage in stages:
            self.db_cur.execute('SELECT code_content FROM code_block WHERE id=%s;', (stage, ))
            full_job_file_db = json.loads(self.db_cur.fetchone()['code_content'], strict=False)
            # print('\n\n\n\n')
            # print(full_job_file_db)
            # print('\n\n\n\n')
            full_job_file += full_job_file_db['code']

        # Output
        self.db_cur.execute('SELECT * FROM code_block_templates WHERE template_name=%s;', ('pipeline_execution', ))
        pipeline_execution = self.db_cur.fetchone()['code_content']

        self.db_cur.execute('SELECT * FROM code_block_templates WHERE template_name=%s;', ('output', ))
        output = self.db_cur.fetchone()['code_content']

        full_job_file += pipeline_execution['code']
        print('\n\n\n\n\n')
        print(output['code'])
        print('\n\n\n\n\n')
        full_job_file += output['code'].format(user_email="user_"+str(self.current_user["id"]),  application_id="application_"+str(application["id"]), model_name="{model_name}")

        return full_job_file

    def _upload_emr_files(self, job_file, prereq_file, application_json, application_id):
        """UPLOAD files and return url"""
        import urllib

        prereq_file_url = "{user}/application_{application_id}/prerequisites_{application_id}.sh".\
            format(user="user_" + str(self.current_user["id"]), application_id=application_id)
        job_file_url = "{user}/application_{application_id}/job_{application_id}.py".\
            format(user="user_" + str(self.current_user["id"]), application_id=application_id)

        s3_client, _ = self.start_s3_connection()

        s3_client.put_object\
        (\
            ACL="public-read-write",\
            Bucket=self.BUCKET_SPARK_JOBS,\
            Body=job_file,\
            Key=job_file_url
        )

        s3_client.put_object\
        (\
            ACL="public-read-write",\
            Bucket=self.BUCKET_SPARK_JOBS,\
            Body=prereq_file,\
            Key=prereq_file_url
        )

        job_file_url = "s3://" + self.BUCKET_SPARK_JOBS + "/" + job_file_url
        prereq_file_url = "s3://" + self.BUCKET_SPARK_JOBS + "/" + urllib.parse.quote(prereq_file_url)
        return job_file_url, prereq_file_url

    def _deploy_emr_application_training(self, application, job_file_url, prereq_file_url):
        """DEPLOT application on cluster"""

        elements_to_replace = {
            "user": "user_" + str(self.current_user["id"]),
            "spark-job": job_file_url,
            "application_id": application["id"],
            "preconfig_script": prereq_file_url,
            "job_id": application["id"]
        }

        job_step_content = self._create_job_json_from_template(\
        elements_to_replace=elements_to_replace)
        # print('\n\n\n\n\n\n')
        # print('#########################')
        # import pprint
        # pprint.pprint(job_step_content)
        # print('#########################')
        # print('\n\n\n\n\n\n')
        emr_client = self.start_emr_connection()
        result = emr_client.run_job_flow(**job_step_content)
        print("\n\n\n\n\n\n\n", result, "\n\n\n\n\n")

    def _create_emr_files(self, application):
        """CREATE files and return content"""
        job_file = self._create_application_job_file(application)

        elements_to_replace = {}
        application_training_json = self._create_job_json_from_template(\
        elements_to_replace=elements_to_replace)

        job_file_url = self.BUCKET_SPARK_JOBS + "/{user}/application_{application_id}/job_{application_id}.py".\
            format(user="user_" + str(self.current_user["id"]), application_id=application['id'])
        prereq_file = self._create_prerequisites_from_template(job_file_url)

        return job_file, prereq_file, application_training_json

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

        job_file, prereq_file, application_training_json = self._create_emr_files(application)

        job_file_url, prereq_file_url = self._upload_emr_files(\
        job_file, prereq_file, application_training_json, application_id)
        self._deploy_emr_application_training(application, job_file_url, prereq_file_url)
        # self.db_cur.execute\
        # (\
        #     "UPDATE applications SET application_status=%s WHERE id=%s;",\
        #     ("training", application_id)
        # )
        # self.db_conn.commit()
# UPDATE APPLICATION STATUS
        self.db_cur.execute(\
        "UPDATE applications SET application_status='training' WHERE id=%s;",\
        (application_id, ))
        self.db_conn.commit()
        self.redirect(self.get_argument("next", "/ml_models"))
