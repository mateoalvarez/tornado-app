"""Home page handlers"""
import logging
import tornado
from tornado import gen
import json
from ..base.handlers import BaseHandler

LOGGER = logging.getLogger(__name__)

class PipelinesHandler(BaseHandler):
    """ Home page pipeline """

    @gen.coroutine
    @tornado.web.authenticated
    def get(self):
        """GET method on pipeline page"""
        self.render(
            "pipelines/pipelines.html",
                    )
