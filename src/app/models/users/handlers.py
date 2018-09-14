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
        email = self.get_argument("email", "")
        if user_exists(self.db_cur, email):
            raise tornado.web.HTTPError(400, "User already exists")

        executor = concurrent.futures.ThreadPoolExecutor(2)
        hashed_password = yield executor.submit(
            bcrypt.hashpw, tornado.escape.utf8(self.get_argument("password")),
            bcrypt.gensalt())

        user_type = 1
        self.db_cur.execute(
            "INSERT INTO users (email, name, hashed_password, type)\
                VALUES (%s, %s, %s, %s);", (
                email,
                self.get_argument("username"),
                hashed_password.decode('utf-8'),
                user_type)
        )
        self.db_conn.commit()
        user = get_user(self.db_cur, email)
        self.set_current_user(str(user["id"]))
        print(self.current_user)
        self.redirect(self.get_argument("next", "/"))


class LoginHandler(BaseHandler):
    """User Login Handler"""
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
        if self.get_current_user():
            self.redirect(self.get_argument("next", "/"))
        self.render("users/login.html", next=self.get_argument("next", "/"))

    @gen.coroutine
    def post(self):
        """User login post"""
        user = get_user(self.db_cur, self.get_argument("email", ""))
        if user and bcrypt.checkpw(
            self.get_argument("password").encode(),
                user["hashed_password"].encode()):
            self.set_current_user(str(user["id"]))
            self.redirect(
                self.get_argument("next", "/")
                )
        else:
            self.render("users/login.html",
                        next=self.get_argument("next", "/"),
                        error_message="Incorrect email or password")


class LogoutHandler(BaseHandler):
    """User logout Handler"""

    @gen.coroutine
    def get(self):
        """GET logout"""
        self.clear_cookie("user")
        self.redirect(
            self.get_argument("next", "/"))


class UserSettingsHandler(BaseHandler):
    """User settings page handler"""

    @gen.coroutine
    @tornado.web.authenticated
    def get(self):
        """GET user settings page"""

        self.db_cur.execute(
            "SELECT name, email, type FROM users WHERE id=%s;",
            (str(self.current_user["id"]),))
        user_data = self.db_cur.fetchone()

        self.db_cur.execute(
            "SELECT * FROM datasource_settings WHERE user_id=%s;",
            (str(self.current_user["id"])))
        all_twitter_settings = self.db_cur.fetchall()

        user_twitter_settings = []
        for configuration in all_twitter_settings:
            user_twitter_settings.append(
                configuration["datasource_access_settings"])

        self.render("users/settings.html",
                    user_data=user_data,
                    user_twitter_settings=user_twitter_settings)


class UserDatasourcesHandler(BaseHandler):
    """ Users DataSources page handler """

    def get_datasources(self, db_cur, user):
        """ method for retrieve datasources filtered by user
        # datasource_settings
        # type:
        # 1 - Twitter
        # datasource_access_settings {consumer_key:"", consumer_secret:"", access_key:"", access_secret:""}
        """
        db_cur.execute("""SELECT id, type, datasource_access_settings
                        FROM datasource_settings
                        WHERE user_id=%s;""", (str(user["id"]),))
        datasources = db_cur.fetchall()

        return datasources

    def put_datasource(self, db_cur, db_conn, user, datasource):
        """ Method to store datasource in database """

        db_cur.execute(
            """INSERT INTO datasource_settings (user_id, type, datasource_access_settings)\
            VALUES (%s, %s, %s);""",
            (user["id"],
             datasource["type"],
             datasource["datasource_access_settings"]))
        try:
            db_conn.commit()
        except Exception as e:
            db_conn.rollback()
            LOGGER.error("There was an error in INSERT process into datasource_settings table")
            LOGGER.error(e)

    def update_datasource(self, db_cur, db_conn, user, datasource):
        """ Method to update datasource information """
        db_cur.execute(
            """UPDATE datasource_settings
            SET type=%s, datasource_access_settings=%s
            WHERE user_id=%s AND id=%s;""",
            (datasource["type"],
             datasource["datasource_access_settings"],
             user["id"],
             datasource["id"]))
        try:
            db_conn.commit()
        except Exception as e:
            db_conn.rollback()
            LOGGER.error("There was an error in UPDATE process into datasource_settings table")
            LOGGER.error(e)

    def delete_datasource(self, db_cur, db_conn, user, datasource):
        db_cur.execute(
            """DELETE FROM datasource_access_settings WHERE id=%s AND user_id=%s;""",
            (datasource["id"], user["id"]))
        try:
            db_conn.commit()
        except Exception as e:
            db_conn.rollback()
            LOGGER.error("There was an error in DELETE process from datasource_settings table")
            LOGGER.error(e)


class UserDatasourcesConfigHandler(BaseHandler):
    """ Users DataSources COnfig Handler"""

    def get_datasource_config(self, db_cur, id_datasource):
        LOGGER.debug("Going to SELECT datasource_configuration from datasource_application_config")
        db_cur.execute(
            """SELECT id, datasource_application_config
            FROM datasource_configurations
            WHERE datasource_settings_id=%s;""",
            (id_datasource,))
        datasource_config = db_cur.fetchone()
        return datasource_config

    def put_datasource_config(self, db_cur, db_conn, id_datasource, datasource_config):
        LOGGER.debug("Going INSERT datasource_configuration into datasource_application_config")
        db_cur.execute(
            """INSERT INTO datasource_configurations (datasource_settings_id,
            datasource_application_config) VALUES (%s, %s);""",
            (id_datasource, datasource_config))
        try:
            db_conn.commit()
        except Exception as e:
            db_conn.rollback()
            LOGGER.error("There was an error in INSERT process into datasource_configurations table")
            LOGGER.error(e)

    def update_datasource_config(self, db_cur, db_conn, id_datasource_config, datasource_config):
        LOGGER.debug("Going to UPDATE datasource_configuration in datasource_application_config")
        db_cur.execute(
            """UPDATE datasource_configurations SET datasource_application_config=%s
            WHERE id=%s;""",
            (datasource_config,
             id_datasource_config))
        try:
            db_conn.commit()
        except Exception as e:
            db_conn.rollback()
            LOGGER.error("There was an error in UPDATE process into datasource_configurations table")
            LOGGER.error(e)

    def delete_datasource_config(self, db_cur, db_conn, id_datasource_config, id_datasource):
        LOGGER.debug("Going to DELETE datasource_configuration from datasource_application_config")
        db_cur.execute(
            """DELETE FROM datasource_configurations
            WHERE id=%s AND datasource_settings_id=%s;""",
            (id_datasource_config, id_datasource))
        try:
            db_conn.commit()
        except Exception as e:
            db_conn.rollback()
            LOGGER.error("There was an error in DELETE process from datasource_settings table")
            LOGGER.error(e)
