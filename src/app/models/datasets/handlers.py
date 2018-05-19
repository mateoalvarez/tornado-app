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

    def _save_dataset_in_database(self, dataset_name, storage_url):
        """Store dataset references on database"""
        self.db_cur.execute\
        (\
            "INSERT INTO datasets (user_id, dataset_name, storage_url) VALUES (%s,%s,%s);",
            (self.current_user["id"], dataset_name, storage_url)
        )
        self.db_conn.commit()

    def _get_dataset_from_database_by_s3_key(self, user_id, s3_key):
        self.db_cur.execute(
            "SELECT id FROM datasets WHERE user_id = %(user_id)s AND storage_url LIKE %(s3_key)s;",
            {"user_id":user_id, "s3_key":'%'+s3_key}
        )
        datasets = self.db_cur.fetchall()
        return datasets

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
                aux_user_dataset = user_dataset_s3
                db_user_datasets = self._get_dataset_from_database_by_s3_key(self.current_user["id"], aux_user_dataset["Key"])
                if bool(db_user_datasets):
                    aux_user_dataset.update(db_user_datasets[0])
                    user_datasets.append(aux_user_dataset)

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
                object_acl = self.S3_RESOURCE.ObjectAcl(\
                bucket_name=self.BUCKET_DATASETS,\
                object_key=self.current_user["email"] + "/" + filename
                )
                response = object_acl.put(ACL='public-read')
                self._save_dataset_in_database(info['filename'], "s3://{bucket}/{directory}"\
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
        self.db_conn.commit()

    def _get_dataset_from_database_by_id(self, user_id, dataset_id):
        self.db_cur.execute(
            "SELECT * FROM datasets WHERE user_id = %s AND id = %s;",
            (self.current_user["id"], dataset_id)
        )
        dataset = self.db_cur.fetchone()
        return dataset

    @gen.coroutine
    @tornado.web.authenticated
    def post(self):
        """DELETE file from s3 bucket"""
        dataset_id_to_delete = int(self.get_argument("dataset", ""))
        # get information from database about dataset using dataset_id obtained from request
        dataset_from_db = self._get_dataset_from_database_by_id(self.current_user["id"], dataset_id_to_delete)
        if dataset_from_db != None:
            self._delete_dataset(dataset_id_to_delete)
            s3_dataset_key = "{s3_bucket_prefix}/{s3_resource}".format(s3_bucket_prefix=self.current_user["email"], s3_resource=dataset_from_db["dataset_name"])
            self.S3_CLIENT.delete_object\
            (\
                Bucket=self.BUCKET_DATASETS,
                Key=s3_dataset_key \
            )
        else:
            LOGGER.warning("There is any dataset in database with id {dataset_id} for user {user_id}".format(dataset_id=dataset_id_to_delete, user_id=self.current_user["id"]))
        self.redirect(self.get_argument("next", "/datasets"))
