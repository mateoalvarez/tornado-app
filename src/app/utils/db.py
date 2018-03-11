"""Data base management and connection"""
import asyncio

import time
import logging
from tornado.ioloop import IOLoop

import asyncpg

logger = logging.getLogger(__name__)

def get_db():
    return getattr(IOLoop.current(), 'app_instance').settings['db']

async def connect_psql(psql_settings, **kwargs):
    psql_address = kwargs.get("psql_address",
    {
        'host': psql_settings['host'],
        'port': psql_settings['port'],
    })
    psql_db = kwargs.get('psql_db', psql_settings['db_name'])
    db = None
    for i in xrange(psql_settings['reconnect_tries'] + 1):
        try:
            db = await asyncpg.connect(
                user = 'postgres',
                password = 'mysecretpassword',
                database = 'twitter_app_db',
                host = 'localhost',
                port = 32768
            )
        except ConnectionError:
            if i >= psql_settings['reconnect_tries']:
                raise
            else:
                timeout = psql_settings['reconnect_timeout']
                logger.warning("Connection Failure #{0} during server start, waiting {1} seconds".format(i + 1, timeout))
                time.sleep(timeout)
        else:
            break
    return db
