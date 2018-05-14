"""Main web handlers, from tornado web handler"""

import logging
import psycopg2
from psycopg2.extras import RealDictCursor
# import json
# import jinja2 as jinja
import os

import tornado.web
import boto3
import requests
import kubernetes
# from tornado import gen

LOGGER = logging.getLogger(__name__)

class BaseHandler(tornado.web.RequestHandler):
    """
        Class to collect all common handler methods.
        Extend all other handlers from this one
    """
    def get_current_user(self):
        """Returns the user cookie"""
        user_id = self.get_secure_cookie("user")
        if not user_id:
            return None
        self.db_cur.execute("SELECT * FROM users WHERE id=%s;", (user_id.decode("utf-8"),))
        return self.db_cur.fetchone()

    def get_current_user_session(self):
        """Obtain user session"""
        return self.get_secure_cookie("user")

    def set_current_user(self, user):
        """Aux function to create user cookie"""
        if user:
            self.set_secure_cookie("user", user)
        else:
            self.clear_cookie("user")
        return

    def initialize(self, **kwargs):
        """Start database"""
        super(BaseHandler, self).initialize(**kwargs)
        # self.db = self.settings['db']
        self.db_conn = psycopg2.connect(\
            "dbname={database_name} \
            user={database_user} \
            password={database_pass} \
            host={database_host} \
            port={database_port}".format(
                database_name=os.environ.get("DATABASE_NAME", "twitter_app_db"),
                database_user=os.environ.get("DATABASE_USER", "postgres"),
                database_pass=os.environ.get("DATABASE_PASS", "mysecretpassword"),
                database_host=os.environ.get("DATABASE_HOST", "localhost"),
                database_port=os.environ.get("DATABASE_PORT", "32769")))
        self.db_cur = self.db_conn.cursor(cursor_factory=RealDictCursor)

        """S3 variables"""
        self.AWS_REGION = os.environ.get("AWS_REGION", "eu-central-1")

        self.BUCKET_DATASETS = os.environ.get("BUCKET_DATASET", "tornado-app-datasets")
        self.BUCKET_DATASETS_REGION = os.environ.get("BUCKET_DATASETS_REGION", self.AWS_REGION)

        self.BUCKET_YAML_TEMPLATES = os.environ.get("BUCKET_YAML_TEMPLATES", "tornado-app-k8s-templates")
        self.BUCKET_YAML_TEMPLATES_REGION = os.environ.get("BUCKET_YAML_TEMPLATES_REGION", self.AWS_REGION)

        self.BUCKET_SPARK_JOBS = os.environ.get("BUCKET_SPARK_JOBS", "tornado-app-emr")
        self.BUCKET_SPARK_JOBS_REGION = os.environ.get("BUCKET_SPARK_JOBS_REGION", self.AWS_REGION)

        k8s_config_file = open("k8s_config", "w")
        k8s_config_file.write(requests.get("https://s3." + self.BUCKET_YAML_TEMPLATES_REGION + ".amazonaws.com/" + self.BUCKET_YAML_TEMPLATES + "/k8s-config/pyxis-k8s.config").content.decode("utf-8"))
        k8s_config_file.close()
        self.k8s_config = kubernetes.config.load_kube_config("k8s_config")
        self.k8s_namespace = 'default'

    """S3 variables"""
    AWS_REGION = os.environ.get("AWS_REGION", "eu-central-1")

    BUCKET_DATASETS = os.environ.get("BUCKET_DATASET", "tornado-app-datasets")
    BUCKET_DATASETS_REGION = os.environ.get("BUCKET_DATASETS_REGION", AWS_REGION)

    BUCKET_YAML_TEMPLATES = os.environ.get("BUCKET_YAML_TEMPLATES", "tornado-app-k8s-templates")
    BUCKET_YAML_TEMPLATES_REGION = os.environ.get("BUCKET_YAML_TEMPLATES_REGION", AWS_REGION)

    BUCKET_SPARK_JOBS = os.environ.get("BUCKET_SPARK_JOBS", "tornado-app-emr")
    BUCKET_SPARK_JOBS_REGION = os.environ.get("BUCKET_SPARK_JOBS_REGION", AWS_REGION)

    @staticmethod
    def start_s3_connection():
        """Configure AWS credentials"""

        s3_client = boto3.client("s3", region_name=os.environ.get("BUCKET_DATASETS_REGION", "eu-central-1"))
        s3_resource = boto3.resource("s3", region_name=os.environ.get("BUCKET_DATASETS_REGION", "eu-central-1"))

        return s3_client, s3_resource

    @staticmethod
    def start_emr_connection():
        """Configure AWS credentials"""
        emr_client = boto3.client("emr", region_name=os.environ.get("BUCKET_SPARK_JOBS_REGION", "eu-central-1"))

        return emr_client
