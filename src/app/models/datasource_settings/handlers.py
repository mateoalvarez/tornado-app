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
        datasource_settings = json.dumps(\
        {element: self.get_argument(element) for element in self.request.arguments})
        print('\n\n\n')
        from pprint import pprint
        pprint(datasource_settings)
        print('\n\n\n')
        self.db_cur.execute(\
        "INSERT INTO datasource_settings (user_id, type, datasource_access_settings)\
         VALUES (%s, %s, %s);", (str(self.current_user["id"]), 1, datasource_settings))
        self.db_conn.commit()
        self.redirect("/user_settings")
