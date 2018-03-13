"""Runnning applications handlers"""
import logging
import tornado
from tornado import gen
from ..base.handlers import BaseHandler

LOGGER = logging.getLogger(__name__)

class RunningApplicationsHandler(BaseHandler):
    """Running applications handler """
    @gen.coroutine
    def get(self):
        """GET method"""
        self.render("running_applications/running_applications.html")
