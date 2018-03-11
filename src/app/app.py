"""Main class"""
# -*- coding: utf-8 -*-
import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado.options import options
from settings import settings, PSQL_DB
from urls import URL_PATTERNS
from utils.db import connect_psql

class TwitterApplication(tornado.web.Application):
    """Web application class"""
    def __init__(self, *args, **kwargs):
        db = connect_psql(PSQL_DB, **kwargs)
        super(TwitterApplication, self).__init__(
            URL_PATTERNS, db=db, *args, **dict(settings, **kwargs)
        )

def main():
    """Server starter"""
    app = TwitterApplication()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
