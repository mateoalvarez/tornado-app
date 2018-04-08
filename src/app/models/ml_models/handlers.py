"""Home page handlers"""
import logging
import tornado
import tornado
from tornado import gen
import json
import requests
from .aws_deploy_handler import MLModelsAWSDeployHandler
from .job_builder import JobAssemblerHandler
from ..base.handlers import BaseHandler


LOGGER = logging.getLogger(__name__)

class MLModelsHandler(BaseHandler):
    """ Home page handler """
# Aux functions



    def _get_user_applications(self):
        """GET user's pipelines"""
        self.db_cur.execute\
        (\
            "SELECT * FROM applications WHERE user_id=%s;", (self.current_user["id"],)\
        )
        applications = self.db_cur.fetchall()
        return applications
    def _get_initializers(self):
        """GET initializer code blocks"""
        self.db_cur.execute\
        (\
            "SELECT * FROM code_block_templates where type='input';"\
        )
        initializers = self.db_cur.fetchall()
        return initializers

    def _get_data_prep_methods(self):
        """GET preprocessing methods"""
        self.db_cur.execute\
        (\
            "SELECT * FROM code_block_templates where type='preprocessing';"\
        )
        data_prep_methods = self.db_cur.fetchall()
        return data_prep_methods

    def _get_models(self):
        """GET models"""
        self.db_cur.execute\
        (\
            "SELECT * FROM code_block_templates where type='model';"
        )
        models = self.db_cur.fetchall()
        return models

    def _get_outputs(self):
        """GET output code blocks"""
        self.db_cur.execute\
        (\
            "SELECT * FROM code_block_templates where type='output';"\
        )
        outputs = self.db_cur.fetchall()
        return outputs

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
        user_applications = self._get_user_applications()
        datasets = self._get_datasets()
        classification_criteria = self._get_classification_criteria()

        self.render\
        (\
            "ml_models/ml_models.html",\
            datasets=datasets,\
            data_prep_methods=data_prep_methods,\
            user_applications=user_applications,\
            models=models,\
            classification_criteria=classification_criteria
        )

    @gen.coroutine
    @tornado.web.authenticated
    def post(self):
        """CREATE and deploy training works"""

        # substitutes the config values
        dataset = self.get_argument('application_dataset')
        preprocessing_blocks = self.get_argument('application_prep_stages_ids')
        preprocessing_blocks_config = self.get_argument('application_prep_stages_config', '')
        model_blocks = self.get_argument('application_models_ids')
        model_blocks_config = self.get_argument('application_models_config', '')

        # print('\n\n\n')
        # print(model_blocks)
        # print(dataset)
        # print('\n\n\n')

        # Create block codes
        assembler_class = JobAssemblerHandler(self.db_cur, self.current_user)

        dataset_url = assembler_class._get_dataset_from_db(dataset)[0]["storage_url"]
        initializer_ids = assembler_class._get_code_block_template_by_type("input")
        initializer_configs = [{"dataset": dataset_url}]
        for initializer, initializer_config in zip(initializer_ids, initializer_configs):
            initializer_ids.append(assembler_class._create_code_block(initializer["id"], initializer_config))

        preprocessing_block_ids = []
        for preprocessing_block, preprocessing_block_config in zip(preprocessing_blocks, preprocessing_blocks_config):
            preprocessing_block_ids.append(assembler_class._create_code_block(preprocessing_block, preprocessing_block_config))

        model_block_ids = []
        for model_block, model_block_config in zip(model_blocks, model_blocks_config):
            model_block_ids.append(assembler_class._create_code_block(model_block, model_block_config))

        print("################################", preprocessing_block_ids)
        self.db_cur.execute\
        (\
            "INSERT INTO applications (user_id, application_name, training_config_resources, application_dataset, application_prep_stages_ids, application_models_ids, classification_criteria, application_status, error_status) VALUES (%s, %s, %s, %s, ARRAY[%s], ARRAY[%s], %s, %s, %s);", \
            (\
                self.current_user['id'],\
                self.get_argument('application_name', ''),\
                self.get_argument('training_config_resources', ''),\
                dataset,\
                ','.join(map(str, preprocessing_block_ids)),\
                ','.join(map(str, model_block_ids)),\
                self.get_argument('classification_criteria', ''),\
                'untrained',\
                ''\
            )
        )
        self.db_conn.commit()

        self.redirect(self.get_argument("next", "/ml_models"))
