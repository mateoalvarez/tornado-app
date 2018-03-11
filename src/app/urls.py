"""Webpage urls and handlers"""

from tornado.web import url

from models.home.handlers import HomeHandler
from models.users.handlers import RegisterHandler, LogoutHandler, LoginHandler

URL_PATTERNS = [
    # Home
    url(r"/", HomeHandler, name="home"),

    # Auth
    url(r"/auth/register", RegisterHandler, name="register"),
    url(r"/auth/login", LoginHandler, name="login"),
    url(r"/auth/logout", LogoutHandler, name="logout"),

    #

]
