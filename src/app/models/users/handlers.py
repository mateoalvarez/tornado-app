"""User handlers"""

import logging
import concurrent.futures
import bcrypt
import tornado
from tornado import gen
from ..base.handlers import BaseHandler

LOGGER = logging.getLogger(__name__)

def user_exists(db_cur, email):
    """Check if user exists on database"""
    return bool(get_user(db_cur, email))

def get_user(db_cur, email):
    """GET user from database"""
    db_cur.execute("SELECT * FROM users WHERE email=%s;", (email,))
    return db_cur.fetchone()

class RegisterHandler(BaseHandler):
    """User Registration Handler"""
    @gen.coroutine
    def get(self):
        """User registration page"""
        self.render("users/registration.html")

    @gen.coroutine
    def post(self):
        """User registration creation"""

        if user_exists(self.db_cur, self.get_argument("email", "")):
            # self.render("users/registration.html", error="400, User already exists")
            raise tornado.web.HTTPError(400, "User already exists")

        executor = concurrent.futures.ThreadPoolExecutor(2)
        hashed_password = yield executor.submit(
            bcrypt.hashpw, tornado.escape.utf8(self.get_argument("password")),
            bcrypt.gensalt())

        user_type = 1
        user_id = self.db_cur.execute(
            "INSERT INTO users (email, name, hashed_password, type)\
                VALUES (%s, %s, %s, %s);", (\
                self.get_argument("email"),
                self.get_argument("username"),
                hashed_password.decode('utf-8'),
                user_type)
        )
        self.db_conn.commit()
        self.set_secure_cookie("user", str(user_id))
        self.redirect(self.get_argument("next", "/"))





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

        user = get_user(self.db_cur, self.get_argument("email", ""))

        if user and bcrypt.checkpw(self.get_argument("password").encode(), user["hashed_password"].encode()):
            self.set_current_user(user["id"])
            self.redirect(self.get_argument("next", u"/"))
        else:
            self.render("users/login.html", error="Incorrect email or password")
            print("error login")
            return




class LogoutHandler(BaseHandler):
    """User logout Handler"""

    @gen.coroutine
    def get(self):
        """GET logout"""

    @gen.coroutine
    def delete(self):
        """DELETE user session"""
