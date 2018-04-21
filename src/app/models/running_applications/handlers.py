"""Runnning applications handlers"""
import logging
import tornado
from tornado import gen
from ..base.handlers import BaseHandler

LOGGER = logging.getLogger(__name__)

class RunningApplicationsHandler(BaseHandler):
    """Running applications handler """

    def get_applications_list(self, db_cur, user):
        db_cur.execute("""SELECT id, application_name, application_status
                        FROM applications
                        WHERE user_id=%s;""", (str(user["id"]),))
        applications = db_cur.fetchall()
        return applications

    def put_applications(self, db_cur, db_conn, user, application):
        """ Method to store application in database """
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

    def delete_applications(self, db_cur, db_conn, user, applications):
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
    def get(self):
        """GET method"""
        self.render("running_applications/running_applications.html")
