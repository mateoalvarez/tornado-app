import logging
import tornado
from tornado import gen
import json
# import requests
import botocore
# from .aws_deploy_handler import MLModelsAWSDeployHandler
from .job_builder import JobAssemblerHandler
from ..base.handlers import BaseHandler


LOGGER = logging.getLogger(__name__)


class MLModelsHandler(BaseHandler):
    """ Home page handler """
# Aux functions

    def _get_user_pipelines(self):
        """GET user's pipelines"""
        self.db_cur.execute(
            "SELECT * FROM pipeline WHERE user_id=%s;",
            (self.current_user["id"],)
        )
        pipelines = self.db_cur.fetchall()
        return pipelines

    def _get_user_pipelines_ids(self):
        """GET user's pipelines"""
        self.db_cur.execute(
            "SELECT 'id' FROM pipelines WHERE user_id=%s;",
            (self.current_user["id"],)
        )
        pipelines_ids = self.db_cur.fetchall()
        return pipelines_ids

    def _get_initializers(self):
        """GET initializer code blocks"""
        self.db_cur.execute(
            "SELECT * FROM code_block_templates where type='input';"
        )
        initializers = self.db_cur.fetchall()
        return initializers

    def _get_data_prep_methods(self):
        """GET preprocessing methods"""
        self.db_cur.execute(
            "SELECT * FROM code_block_templates where type='preprocessing';"
        )
        data_prep_methods = self.db_cur.fetchall()
        return data_prep_methods

    def _get_models(self):
        """GET models"""
        self.db_cur.execute(
            "SELECT * FROM code_block_templates where type='model';"
        )
        models = self.db_cur.fetchall()
        return models

    def _get_outputs(self):
        """GET output code blocks"""
        self.db_cur.execute(
            "SELECT * FROM code_block_templates where type='output';"
        )
        outputs = self.db_cur.fetchall()
        return outputs

    def _get_datasets(self):
        """GET all datasets from user and public"""
        self.db_cur.execute(
            "SELECT * FROM datasets;"
        )
        datasets = self.db_cur.fetchall()
        return datasets

    def _get_classification_criteria(self):
        """GET classification_criteria"""
        self.db_cur.execute(
            "SELECT * FROM classification_criteria;"
        )
        classification_criteria = self.db_cur.fetchall()
        return classification_criteria

    def _update_pipeline_training_status(self, pipeline_id):
        """GET to S3 to check finished pipeline training"""
        _, s3_resource = self.start_s3_connection()

        pipeline_results_url = "user_" + str(self.current_user["id"]) + \
            "/models/pipeline_" + str(pipeline_id) + "/preprocessing.zip"
        print('RESULTS ##########')
        print(pipeline_results_url)
        try:
            s3_resource.Object(
                self.BUCKET_SPARK_JOBS, pipeline_results_url).load()
            self.db_cur.execute(
                "UPDATE pipelines SET pipeline_status='trained' WHERE id=%s;",
                (pipeline_id,))
            self.db_conn.commit()
        except botocore.exceptions.ClientError as exception:
            if exception.response['Error']['Code'] == "404":
                pass
            else:
                # Throw error
                pass
# Handler methods

    @gen.coroutine
    @tornado.web.authenticated
    def get(self):
        """GET method on dataset page"""

        data_prep_methods = self._get_data_prep_methods()
        models = self._get_models()
        user_pipelines = self._get_user_pipelines()
        datasets = self._get_datasets()
        input_methods = self._get_initializers()
        output_methods = self._get_outputs()
        classification_criteria = self._get_classification_criteria()

        model_names = ','.join([model["template_name"] for model in models])
        model_ids = ','.join([str(model["id"]) for model in models])
        preprocessing_names = ','.join([prep["template_name"]
                                        for prep in data_prep_methods])
        preprocessing_ids = ','.join([str(prep["id"])
                                      for prep in data_prep_methods])

        for pipeline in user_pipelines:
            self._update_pipeline_training_status(pipeline_id["id"])

        self.render(
            "ml_models/ml_models.html",
            datasets=datasets,
            input_methods=input_methods,
            data_prep_methods=data_prep_methods,
            user_pipelines=user_pipelines,
            models=models,
            output_methods=output_methods,
            classification_criteria=classification_criteria,
            model_names=model_names,
            model_ids=model_ids,
            preprocessing_names=preprocessing_names,
            preprocessing_ids=preprocessing_ids
        )

    @gen.coroutine
    @tornado.web.authenticated
    def post(self):
        """CREATE and deploy training works"""

        # print('\n\n\n')
        # print('POST PARAMS')
        # print(self.request.arguments)
        # print('\n\n\n')

        dataset = self.get_argument('application_dataset', '')

        preprocessing_blocks = list(map(
            int, self.request.arguments['pipeline_prep_stages_ids']))
        preprocessing_blocks_config = self.get_arguments(
            "pipeline_prep_stages_ids_config")

        preprocessing_blocks_config = ["{}" if element == '' else element
                                       for element in preprocessing_blocks_config]

        preprocessing_blocks_full = []
        for block, block_config in zip(preprocessing_blocks, preprocessing_blocks_config):
            preprocessing_blocks_full.append(
                    {
                        "id": block,
                        "config": json.loads(block_config)
                    }
                )

        model_blocks = list(map(
            int, self.request.arguments['application_models_ids']))
        model_blocks_config = self.get_arguments("application_models_config")
        model_blocks_config = ["{}" if element == '' else element
                               for element in model_blocks_config]

        model_blocks_full = []
        for block, block_config in zip(model_blocks, model_blocks_config):
            model_blocks_full.append(
                    {
                        "id": block,
                        "config": json.loads(block_config)
                    }
                )

        # Create block codes

        assembler_class = JobAssemblerHandler(self.db_cur, self.db_conn, self.current_user)

        dataset_url = assembler_class._get_dataset_from_db(dataset)[0]["storage_url"]
        initializer_ids = assembler_class._get_code_block_template_by_type("input")
        initializer_configs = [{"dataset": dataset_url}]
        initializer_block_ids = []
        for initializer, initializer_config in zip(initializer_ids, initializer_configs):
            initializer_block_ids.append(assembler_class._create_code_block(initializer["id"], initializer_config)[0]["id"])

        preprocessing_block_ids = []
        for preprocessing_block_full in preprocessing_blocks_full:
            preprocessing_block_ids.append(assembler_class._create_code_block(
                preprocessing_block_full['id'],
                preprocessing_block_full['config'])
                                           [0]["id"])

        model_block_ids = []
        for model_block_full in model_blocks_full:
            model_block_ids.append(assembler_class._create_code_block(
                model_block_full['id'], model_block_full['config']
                )[0]["id"])

        # print("\n\n\n")
        # print('initializer blocks')
        # print(initializer_block_ids)
        # print('pp blocks')
        # print(preprocessing_block_ids)
        # print('model blocks')
        # print(model_block_ids)
        # print("\n\n\n")
        self.db_cur.execute(
            """INSERT INTO applications(
            user_id, application_name,
            training_config_resources, application_dataset,
            application_prep_stages_ids, application_models_ids,
            classification_criteria, application_status, error_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);""",
            (
                self.current_user['id'],
                self.get_argument('application_name', ''),
                self.get_argument('training_config_resources', '{}'),
                dataset,
                preprocessing_block_ids,
                model_block_ids,
                self.get_argument('classification_criteria', ''),
                'untrained',
                ''
            )
        )
        self.db_conn.commit()

        self.redirect(self.get_argument("next", "/ml_models"))


class MLModelsHandlerDelete(BaseHandler):
    """Handler for delete method in models"""

    def post(self):
        """DELETE applications"""
        id = self.get_argument("id", '')
        try:
            self.db_cur.execute(
                "DELETE FROM applications WHERE id=%s;",
                (id,)
            )
            self.db_conn.commit()
        except Exception as exception:
            print(exception)
        self.redirect(self.get_argument("next", "/ml_models"))
