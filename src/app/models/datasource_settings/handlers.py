"""Home page handlers"""

import json
import logging
import tornado
from tornado import gen
from ..base.handlers import BaseHandler

LOGGER = logging.getLogger(__name__)


class DataSourceSettingsHandler(BaseHandler):
    """ Datasource settings page handler """

    @gen.coroutine
    @tornado.web.authenticated
    def get(self):
        """GET method for datasource settings"""
        self.render("home/home.html")

    @gen.coroutine
    @tornado.web.authenticated
    def post(self):
        """POST method for datasource settings"""
        datasource_settings = json.dumps(
            {element: self.get_argument(element)
                for element in self.request.arguments})
        self.db_cur.execute(
            """INSERT INTO datasource_settings
            (user_id, type, datasource_access_settings)
            VALUES (%s, %s, %s);""",
            (str(self.current_user["id"]), 1, datasource_settings))
        self.db_conn.commit()
        self.redirect("/user_settings")

class DataSourceSettingsHandlerDelete(BaseHandler):
    """Handler for delete"""
    @gen.coroutine
    @tornado.web.authenticated
    def post(self):
        """POST method to delete credentials"""
        id = self.get_argument("id")
        try:
            self.db_cur.execute(
                "DELETE FROM datasource_settings WHERE id=%s;", (id, ))
            self.db_conn.commit()
        except Exception as exception:
            error = exception
            print(error)
        self.redirect(self.get_argument("next", "/user_settings"))
