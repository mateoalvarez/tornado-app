"""Class to assemble block codes to create spark job"""
import logging
import tornado
from tornado import gen
import json
import requests
from ..base.handlers import BaseHandler

LOGGER = logging.getLogger(__name__)

class JobAssemblerHandler():
    """Class to compose the spark jobs"""
    def __init__(self, db_cur, db_conn, current_user):
        """Initializer method"""
        self.db_cur = db_cur
        self.db_conn = db_conn
        self.current_user = current_user

    def _get_dataset_from_db(self, dataset_id):
        """GET dataset from database"""
        self.db_cur.execute\
        (\
            "SELECT * FROM datasets WHERE id=%s", (dataset_id, )\
        )
        dataset = self.db_cur.fetchall()
        return dataset

    def _get_code_block_template(self, code_template_id):
        """GET code element"""
        self.db_cur.execute\
        (\
            "SELECT * FROM code_block_templates WHERE id=%s;", (code_template_id, )\
        )
        code_element = self.db_cur.fetchall()
        return code_element

    def _get_code_block_template_by_type(self, code_template_type):
        """GET templates given types"""
        self.db_cur.execute\
        (\
            "SELECT * FROM code_block_templates WHERE type=%s;", (code_template_type, )\
        )
        code_element = self.db_cur.fetchall()
        return code_element

    def _get_code_block(self, code_block_id):
        """GET block code filled"""
        self.db_cur.execute\
        (\
            "SELECT * FROM code_block WHERE id=%s;", (code_block_id, )\
        )
        code_element = self.db_cur.fetchall()
        return code_element

    def _create_code_block(self, code_block_template_id, replace_dict):
        """Fill template with values"""
        code_element = self._get_code_block_template(code_block_template_id)
        code_content = code_element[0]["code_content"]["code"]
        for element_key, element_arg in replace_dict.items():
            code_content = code_content.replace("<"+element_key+">", element_arg)
        # Now create a new code block filled with user's params

        code_content_json = '{"code": "%s", "params": "%s"}' % (code_content.replace('"', '\\"'), replace_dict)
        self.db_cur.execute\
        (\
            "INSERT INTO code_block (user_id, code_block_template_id, code_content) VALUES (%s, %s, %s) returning id;",
            (\
                self.current_user['id'],
                code_block_template_id,
                code_content_json
            )
        )
        code_content = self.db_cur.fetchall()
        self.db_conn.commit()
        return code_content


    def _code_assembler(self, pipeline_sequence, pipeline_sequence_params):
        """CREATE full job code"""
        job_code = ''

        stages = ['input', 'preprocessing', 'model', 'output']
        self.db_cur.execute("SELECT * FROM code_block_templates WHERE name='initializer';")
        initializer = self.db_cur.fetchone()

        self.db_cur.execute("SELECT * FROM code_block_templates WHERE name='pipeline_execution';")
        pipeline_execution = self.db_cur.fetchone()

        self.db_cur.execute("SELECT * FROM code_block_templates WHERE name='output';")
        output = self.db_cur.fetchone()

        pipeline_sequence = [initializer] + pipeline_sequence + [pipeline_execution, output]
        for stage in stages:
            for action, action_params in zip(pipeline_sequence[stage], pipeline_sequence_params[stage]):
                job_code += self._create_code_block(action, action_params)
