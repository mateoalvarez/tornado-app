"""Database setup"""

# import sys
import inspect
from psycopg2 import connect

import schema

CONN = connect(dbname='twitter_app_db',\
                user='postgres',\
                host='localhost',\
                password='mysecretpassword',\
                port=32768
              )
CUR = CONN.cursor()

for element in inspect.getmembers(schema)[8:]:
    CUR.execute("create table {0} (".format(element[0]) + \
    ", ".join([prop for prop in element[1].values()]) + ");")

CLASSIFIER = inspect.getmembers(schema)[8]
VALUES = [i for i in CLASSIFIER[1].values()]

CUR.execute("""create table {0} (""".format(CLASSIFIER[0]) + ", ".join(VALUES) + """)""")

# conn.rollback()
