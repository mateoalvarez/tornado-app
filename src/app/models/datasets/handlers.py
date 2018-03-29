"""Home page handlers"""
import logging
import tornado
from tornado import gen
import boto3
from ..base.handlers import BaseHandler

LOGGER = logging.getLogger(__name__)

class DatasetsHandler(BaseHandler):
    """ Home page handler """

    S3_CLIENT, S3_RESOURCE = BaseHandler.start_s3_connection()

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
        if public_datasets_s3["KeyCount"] > 0:
            for public_dataset_s3 in public_datasets_s3["Contents"]:
                public_datasets.append(public_dataset_s3)
        # First element is the root element in case of public_datasets, not necessary for the user
        self.render("datasets/dataset.html",\
                     user_datasets=user_datasets,\
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

    S3_CLIENT, S3_RESOURCE = BaseHandler.start_s3_connection()

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
