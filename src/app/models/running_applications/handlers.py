"""Runnning applications handlers"""
import logging
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
        running_apps = self._get_running_applications(self.db_cur, self.current_user)

        print(" -> running_apps ---- ")
        print(running_apps)
        print(" ---- running_apps <- ")

        self.render("running_applications/running_applications.html", running_applications=running_apps)

class VisualizeApplicationsHandler(BaseHandler):
    """ Handler to manage visualize running application """


    @gen.coroutine
    @tornado.web.authenticated
    def get(self):
        LOGGER.info("Going to retrieve information from MongoDB in order to render it in client browser")
        application_name = self.get_argument("app_name", "aaa")
        last_elements = self.get_argument("elements", "0")
        LOGGER.debug("Application name: {name}".format(name=application_name))
        LOGGER.debug("Elements to show: {elements}".format(elements=last_elements))
        if application_name == "":
            self.render("running_applications/ml_models_visualization.html", records=[])
        else:
            ############################################################
            # Overriding application name only for development purposes,
            # it should be changed before to open PR
            ############################################################
            application_name = "mock_collection"
            ############################################################
            # TODO Filter for those that match with timestamp filter
            records_to_show = list(self._mongo_database[application_name].find())
            self.render("running_applications/ml_models_visualization.html", records=records_to_show)