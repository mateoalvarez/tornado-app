"""Home page handlers"""
import logging
import tornado
from tornado import gen
from ..base.handlers import BaseHandler

LOGGER = logging.getLogger(__name__)

class MLModelsHandler(BaseHandler):
    """ Home page handler """
    @gen.coroutine
    def get(self):
        "GET method on dataset page"
        elementos = ["aaaaaa", "bbbbbbb", "ccccc"]
        self.render("ml_models/ml_models.html", elementos=elementos)
