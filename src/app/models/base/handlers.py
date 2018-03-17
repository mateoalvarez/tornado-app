"""Main web handlers, from tornado web handler"""

import logging
import psycopg2
from psycopg2.extras import RealDictCursor
# import json
# import jinja2 as jinja

import tornado.web
import boto3
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
            "dbname=twitter_app_db \
            user=postgres \
            password=mysecretpassword \
            host=localhost \
            port=32769"\
        )
        self.db_cur = self.db_conn.cursor(cursor_factory=RealDictCursor)

        self.s3_client, self.s3_resource = self.start_AWS_connection("s3")
        self.emr_client = boto3.client("emr")

    """S3 variables"""

    BUCKET_DATASETS = "tornado-app-datasets"
    BUCKET_SPARK_JOBS = "tornado-app-emr"

    @staticmethod
    def start_AWS_connection(service):
        """Configure AWS credentials"""

        service_client = boto3.client(service)
        service_resource = boto3.resource(service)

        return service_client, service_resource
    @staticmethod
    def start_S3_connection():
        """Configure AWS credentials"""

        s3_client = boto3.client("s3", region_name="eu-west-1")
        s3_resource = boto3.resource("s3", region_name="eu-west-1")

        return s3_client, s3_resource
    @staticmethod
    def start_emr_connection():
        """Configure AWS credentials"""

        emr_client = boto3.client("emr", region_name="eu-west-1")

        return emr_client
        # self.template_name = None

        # def render(self, template, context=None):
    #     """Renders template using jinja2"""
    #     if not context:
    #         context = {}
    #     context.update(self.get_template_namespace())
    #     self.write(jinja)
