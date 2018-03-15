"""Home page handlers"""
import logging
import tornado
from tornado import gen
from tornado.web import RequestHandler
import boto3
import os
from ..base.handlers import BaseHandler

LOGGER = logging.getLogger(__name__)

class DatasetsHandler(BaseHandler):
    """ Home page handler """
    # SUPPORTED_METHODS = RequestHandler.SUPPORTED_METHODS + ('DELETE_DATASET',)

    # boto3.set_stream_logger('boto3.resources', logging.INFO)
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
# First element is the root element, not necessary for the user
        self.render("datasets/dataset.html",\
                     user_datasets=user_datasets[1:],\
                     public_datasets=public_datasets[1:]\
                   )

    @gen.coroutine
    @tornado.web.authenticated
    def post(self):
        """POST file to S3 bucket"""
        for field_name, files in self.request.files.items():
            for info in files:
                filename, content_type = info['filename'], info['content_type']
                body = info['body']

                LOGGER.info('POST "%s" "%s" %d bytes', filename, content_type, len(body))
                print("\n\n\n\n\n\n\n\n\n\n\n ########## \n\n\n\n\n\n")
                self.S3_CLIENT.put_object\
                (\
                    Bucket=self.BUCKET,\
                    Body=body,\
                    Key=self.current_user["email"] + "/" + filename
                )
        self.redirect(self.get_argument("next", "/datasets"))

class DatasetsDeleteHandler(BaseHandler):

    S3_CLIENT = boto3.client('s3')
    S3_RESOURCE = boto3.resource('s3')
    BUCKET = "tornado-app-datasets"

    @gen.coroutine
    @tornado.web.authenticated
    def post(self):
        """DELETE file from s3 bucket"""
        dataset_to_delete = self.get_argument("dataset", "")
        print('##########\n\n\n', dataset_to_delete, '\n\n\n############')
        self.S3_CLIENT.delete_object\
        (\
            Bucket=self.BUCKET,
            Key=dataset_to_delete \
        )
        self.redirect(self.get_argument("next", "/datasets"))
