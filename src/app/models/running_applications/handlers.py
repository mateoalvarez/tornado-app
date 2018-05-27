"""Runnning applications handlers"""
import logging
import json
from bson import ObjectId
import tornado
from tornado import gen
from ..base.handlers import BaseHandler

LOGGER = logging.getLogger(__name__)

class RunningApplicationsHandler(BaseHandler):
    """Running applications handler """

    def _get_applications(self, db_cur, user):
        """This method handles the request to list all applications"""
        db_cur.execute("""SELECT id, application_name, application_status
                        FROM applications
                        WHERE user_id=%s;""", (str(user["id"]),))
        applications = db_cur.fetchall()
        return applications

    def _get_running_applications(self, db_cur, user):
        """This method handles the request to list only running applications"""
        db_cur.execute("""SELECT id, application_name, application_status
                        FROM applications
                        WHERE user_id=%s AND application_status='running';""", (str(user["id"]),))
        applications = db_cur.fetchall()
        return applications

    def _put_application(self, db_cur, db_conn, user, application):
        """ this method handles the registration of a application aplication """
        db_cur.execute("""INSERT INTO applications (user_id,
                                                    application_name,
                                                    training_config_resources,
                                                    application_dataset,
                                                    application_prep_stages_ids,
                                                    application_models_ids,
                                                    classification_criteria,
                                                    application_status,
                                                    datasource_configuration,
                                                    datasource_settings_id)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""", (user["id"], application["training_config_resources"], application["application_dataset"], application["application_prep_stages_ids"], application["application_models_ids"], application["classification_criteria"], application["application_status"], application["datasource_configuration"], application["datasource_settings_id"]))
        try:
            db_conn.commit()
        except Exception as e:
            db_conn.rollback()
            LOGGER.error("There was an error in INSERT process into applications table")
            LOGGER.error(e)

    def _delete_applications(self, db_cur, db_conn, user, applications):
        db_cur.execute("""DELETE FROM
                            applications
                            WHERE id=%s AND user_id=%s;""", (applications["id"], user["id"]))
        try:
            db_conn.commit()
        except Exception as e:
            db_conn.rollback()
            LOGGER.error("There was an error in DELETE process from applications table")
            LOGGER.error(e)


    @gen.coroutine
    @tornado.web.authenticated
    def get(self):
        """GET method
        This method will have an parameter to discover in case it is GET running_application/{id_application}"""

        user = self.current_user
        running_apps = self._get_running_applications(self.db_cur, user)

        print(" -> running_apps ---- ")
        print(running_apps)
        print(" ---- running_apps <- ")

        self.render("running_applications/running_applications.html", running_applications=running_apps)

class VisualizeApplicationsHandler(BaseHandler):
    """ Handler to manage visualize running application """


    @gen.coroutine
    @tornado.web.authenticated
    def get(self):
        """GET visualize data"""
        LOGGER.info("Going to retrieve information from MongoDB in order to render it in client browser")
        application_id = self.get_argument("app_id", "aaa")
        last_elements = self.get_argument("elements", "0")
        LOGGER.debug("Application id: {name}".format(name=application_id))
        LOGGER.debug("Elements to show: {elements}".format(elements=last_elements))
        if application_id == "":
            self.render("running_applications/ml_models_visualization.html", records=[])
        else:
            # TODO Filter for those that match with timestamp filter
            records_to_show = list(self._mongo_client[\
            "user_" + str(self.current_user["id"])]["application_" +\
             str(application_id)].find().sort([("_id", -1)]).limit(int(last_elements)))
            self.render("running_applications/ml_models_visualization.html",\
             records=records_to_show, app_id=application_id)

class DownloadDataHandler(BaseHandler):#, tornado.web.StaticFileHandler):
    """Handler to download data"""
    @gen.coroutine
    @tornado.web.authenticated
    def post(self):
        """POST TO DOWNLOAD DATA FROM MONGODB"""
        application_id = self.get_argument("application_id")
        data = list(self._mongo_client[\
        "user_" + str(self.current_user["id"])]["application_" +\
         str(application_id)].find().sort([("_id", -1)]))
        print('\n\n\n\n')
        # print(json.dumps(data[0]))
        print('\n\n\n\n')
        self.set_header('Content-Type', 'text/json')
        self.set_header('Content-Disposition', 'attachment; filename=export.json')
        try:
            for element in data:
                self.write(JSONEncoder().encode(element))
            self.flush()
            self.finish()
            return
        except Exception as exception:
            print("### ERROR ###")
            print(exception)

class JSONEncoder(json.JSONEncoder):
    """Class to decode json"""
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)
