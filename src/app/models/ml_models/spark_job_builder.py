"""Class to assemble block codes to create spark job"""
import logging
import tornado
from tornado import gen
import json
import requests
from ..base.handlers import BaseHandler

LOGGER = logging.getLogger(__name__)

class SparkJobAssemblerHandler(BaseHandler):
    """Class to compose the spark jobs"""

    def _get_spark_code_block(self, kind, spark_code_id):
        """GET spark code element"""
        self.db_cur.execute\
        (\
            "SELECT * FROM %s WHERE id=%s;", (kind, spark_code_id, )\
        )
        spark_code_element = self.db_cur.fetchall()
        return spark_code_element

    def _check_spark_job_sequence(self, sequence):
        """Check the sequence is correct"""
        correct_spark_sequence = ["initializer", "preprocessing", "model", "output"]

        return set(correct_spark_sequence) == set(sequence)

    def spark_job_assembler(self, spark_job_elements):
        """Compose code chuncks to build a spark job"""

        spark_job = ""

        for element in spark_job_elements:

            spark_element = self._get_spark_code_block(element.id)
            spark_sequence = spark_element.type
            spark_job = spark_job + "\n" + spark_element.script
        if self._check_spark_job_sequence(spark_sequence):
            return spark_job
        else:
            return "ERROR"
