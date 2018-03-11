"""Home page handlers"""
import logging
from tornado import gen
from ..base.handlers import BaseHandler

LOGGER = logging.getLogger(__name__)

class HomeHandler(BaseHandler):
    """ Home page handler """
    @gen.coroutine
    def get(self):
        "GET method on home page"
        self.render("home/home.html")
        # self.render( "/Users/Mat/github/tornado-app/src/app/templates/home/home.html")
