"""Home page handlers"""
import logging
import tornado
from tornado import gen
import json
import requests
from .aws_deploy_handler import MLModelsAWSDeployHandler
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

    # def _get_model(self, id):
    #     """GET one model"""
    #     self.db_cur.execute\
    #     (\
    #         "SELECT * FROM models WHERE id=;", (id,)\
    #     )
    #     model = self.db_cur.fetchall()
    #     return model

    # def _get_prep_method(self, id):
    #     """GET one preprocessing method"""
    #     self.db_cur.execute\
    #     (\
    #         "SELECT * FROM preprocessing_methods WHERE id=%s;", (id, )\
    #     )
    #     preprocessing_method = self.db_cur.fetchall()
    #     return preprocessing_method

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
