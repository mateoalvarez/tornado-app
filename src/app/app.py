"""Main class"""
# -*- coding: utf-8 -*-
import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado.options import options
from settings import settings
from urls import URL_PATTERNS


class TwitterApplication(tornado.web.Application):
    """Web application class"""

    def __init__(self, *args, **kwargs):
        super(TwitterApplication, self).__init__(
            URL_PATTERNS, *args, **dict(settings, **kwargs)
        )


def main():
    """Server starter"""
    MB = 1024 * 1024
    GB = 1024 * MB
    MAX_STREAMED_SIZE = 1*GB
    app = TwitterApplication(debug=True)
    tornado.locale.load_translations(options.locale_dir)
    tornado.locale.set_default_locale(options.default_locale)
    http_server = tornado.httpserver.HTTPServer(
        app, ssl_options=options.ssl_options, max_body_size=MAX_STREAMED_SIZE)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
