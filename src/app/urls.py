from tornado.web import url

# from models.users.handlers import RegisterHandler, LogoutHandler, LoginHandler
from models.home.handlers import HomeHandler

url_patterns = [
    # Home
    url(r"/", HomeHandler, name = "home"),

    # Auth
    # url(r"/register/", RegisterHandler, name = "register"),
    # url(r"/login/", LoginHandler, name = "login"),
    # urL(r"/logout/", LogoutHandler, name = "logout"),

    #

]
