"""Home page handlers"""
import logging
import tornado
from tornado import gen
import boto3
from ..base.handlers import BaseHandler

LOGGER = logging.getLogger(__name__)

class DatasetsHandler(BaseHandler):
    """ Home page handler """

    S3_CLIENT = boto3.client('s3')
    S3_RESOURCE = boto3.resource('s3')
    BUCKET = "tornado-app-datasets"

    @gen.coroutine
    @tornado.web.authenticated
    def get(self):
        """GET method on dataset page"""

        user_datasets_s3 = self.S3_CLIENT.list_objects_v2\
        (\
            Bucket=self.BUCKET,\
            Prefix=self.current_user["email"]
        )
        user_datasets = []
        if user_datasets_s3["KeyCount"] > 0:
            for user_dataset_s3 in user_datasets_s3["Contents"]:
                user_datasets.append(user_dataset_s3)

        public_datasets_s3 = self.S3_CLIENT.list_objects_v2\
        (\
            Bucket=self.BUCKET,
            Prefix="Public"
        )
        public_datasets = []
        for public_dataset_s3 in public_datasets_s3["Contents"]:
            public_datasets.append(public_dataset_s3)

        self.render("datasets/dataset.html",\
                     user_datasets=user_datasets,\
                     public_datasets=public_datasets
                   )

    @gen.coroutine
    @tornado.web.authenticated
    def post(self):
        """POST file to S3 bucket"""
