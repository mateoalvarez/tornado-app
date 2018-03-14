"""Main web handlers, from tornado web handler"""

import logging
import psycopg2
from psycopg2.extras import RealDictCursor
# import json
# import jinja2 as jinja

import tornado.web
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

        self.current_user_object = None
        # self.template_name = None

        # def render(self, template, context=None):
    #     """Renders template using jinja2"""
    #     if not context:
    #         context = {}
    #     context.update(self.get_template_namespace())
    #     self.write(jinja)
