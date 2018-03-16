"""Home page handlers"""
import logging
import tornado
from tornado import gen
import boto3
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
# DEPLOY ON AWS-EMR

    def _start_EMR_connection(self):
        """Configure AWS credentials"""

        EMR_CLIENT = boto3.client('emr')
        EMR_RESOURCE = boto3.resource('emr')

        return EMR_CLIENT, EMR_RESOURCE

    def _preconfigure_EMR_machines(self):
        """Install dependencies for the Spark Job"""

        EMR_CLIENT, EMR_RESOURCE = self._start_EMR_connection()

        

    def _deploy_EMR_pipeline_training(self):
        """DEPLOT pipeline on cluster"""

        EMR_CLIENT, EMR_RESOURCE = self._start_EMR_connection()



    # def _deploy_tensorflow_pipeline_training(self):
    #     """DEPLOY """
    #



# Handler methods

    @gen.coroutine
    @tornado.web.authenticated
    def get(self):
        """GET method on dataset page"""

        data_prep_methods = self._get_data_prep_methods()
        models = self._get_models()
        user_pipelines = self._get_user_pipelines()

        self.render\
        (\
            "ml_models/ml_models.html",\
            data_prep_methods=data_prep_methods,\
            user_pipelines=user_pipelines,\
            models=models
        )

    @gen.coroutine
    @tornado.web.authenticated
    def post(self):
        """CREATE and deploy training works"""
