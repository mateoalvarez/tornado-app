"""User handlers"""
import logging
import tornado
from tornado import gen
from ..base.handlers import BaseHandler

LOGGER = logging.getLogger(__name__)

class RegisterHandler(BaseHandler):
    """User Registration Handler"""
    @gen.coroutine
    def get(self):
        """User registration page"""
        self.render("users/registration.html")

    @gen.coroutine
    def post(self):
        """User registration creation"""
        self.render("users/creation.html")

class LoginHandler(BaseHandler):
    """User Login Handler"""

    def set_current_user(self, user):
        """Aux function to create user cookie"""
        if user:
            self.set_secure_cookie("user", tornado.escape.json_encode(user))
        else:
            self.clear_cookie("user")

    #  to refactor
    @staticmethod
    def check_permission(password, username):
        """Aux function to check access"""
        if username == "admin" and password == "admin":
            return True
        return False

    @gen.coroutine
    def get(self):
        """User login page"""
        self.render("users/login.html")

    @gen.coroutine
    def post(self):
        """User login post"""
        username = self.get_argument("username", "")
        password = self.get_argument("password", "")
        self.redirect(self.get_argument("next", u"/"))
        print(username, password)

class LogoutHandler(BaseHandler):
    """User logout Handler"""

    @gen.coroutine
    def get(self):
        """GET logout"""

    @gen.coroutine
    def delete(self):
        """DELETE user session"""
