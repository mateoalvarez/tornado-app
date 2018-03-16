"""Home page handlers"""
import logging
import tornado
from tornado import gen
import boto3
from ..base.handlers import BaseHandler

LOGGER = logging.getLogger(__name__)

class DatasetsHandler(BaseHandler):
    """ Home page handler """
    # SUPPORTED_METHODS = RequestHandler.SUPPORTED_METHODS + ('DELETE_DATASET',)

    def start_AWS_connection(self,service):
        """Configure AWS credentials"""

        service_client = boto3.client(service)
        service_resource = boto3.resource(service)

        return service_client, service_resource
    # boto3.set_stream_logger('boto3.resources', logging.INFO)
    S3_CLIENT, S3_RESOURCE = boto3.client('s3'), boto3.resource('s3')

    def _save_dataset_in_database(self, dataset):
        """Store dataset references on database"""
        self.db_cur.execute\
        (\
            "INSERT INTO datasets (user_id, storage_url) VALUES (%s,%s);",
            (self.current_user["id"], dataset)
        )
        self.db_conn.commit()

    @gen.coroutine
    @tornado.web.authenticated
    def get(self):
        """GET method on dataset page"""

        user_datasets_s3 = self.S3_CLIENT.list_objects_v2\
        (\
            Bucket=self.BUCKET_DATASETS,\
            Prefix=self.current_user["email"]
        )
        user_datasets = []
        if user_datasets_s3["KeyCount"] > 0:
            for user_dataset_s3 in user_datasets_s3["Contents"]:
                user_datasets.append(user_dataset_s3)

        public_datasets_s3 = self.S3_CLIENT.list_objects_v2\
        (\
            Bucket=self.BUCKET_DATASETS,
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
                self.S3_CLIENT.put_object\
                (\
                    Bucket=self.BUCKET_DATASETS,\
                    Body=body,\
                    Key=self.current_user["email"] + "/" + filename
                )
        self._save_dataset_in_database("s3://{bucket}/{directory}"\
        .format(\
            bucket=self.BUCKET_DATASETS,\
            directory=self.current_user["email"] + "/" + filename))
        self.redirect(self.get_argument("next", "/datasets"))

class DatasetsDeleteHandler(BaseHandler):

    S3_CLIENT = boto3.client('s3')
    S3_RESOURCE = boto3.resource('s3')

    def _delete_dataset(self, dataset):
        """DELETE dataset from database"""

        self.db_cur.execute\
        (\
            "DELETE FROM datasets WHERE id=%s",\
            (dataset,)
        )

    @gen.coroutine
    @tornado.web.authenticated
    def post(self):
        """DELETE file from s3 bucket"""
        dataset_to_delete = self.get_argument("dataset", "")
        self.S3_CLIENT.delete_object\
        (\
            Bucket=self.BUCKET_DATASETS,
            Key=dataset_to_delete \
        )
        # TODO DELETE DATASET FROM DATABASE
        self.redirect(self.get_argument("next", "/datasets"))
