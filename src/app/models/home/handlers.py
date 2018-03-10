import logging
from tornado import gen
from ..base.handlers import BaseHandler

logger = logging.getLogger(__name__)

class HomeHandler(BaseHandler):

    @gen.coroutine
    def get(self):
        self.render("home/home.html")
        # self.render( "/Users/Mat/github/tornado-app/src/app/templates/home/home.html")
