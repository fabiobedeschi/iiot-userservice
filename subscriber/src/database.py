from enum import Enum
from logging import getLogger
from os import getenv
from time import sleep

from psycopg2 import connect, Error
from psycopg2.extras import RealDictCursor, RealDictRow

logger = getLogger()


class Fetch(Enum):
    NONE = 0
    ONE = 1
    ALL = -1


class Database:
    def __init__(self, connection=None, connection_conf=None, keep_retrying=False):
        self.connection = connection or Database._init_connection(connection_conf, keep_retrying)

    @staticmethod
    def _init_connection(connection_conf, keep_retrying, backoff=1, backoff_multiplier=2):
        try:
            connection_conf = connection_conf or {
                'user': getenv('POSTGRES_USER'),
                'password': getenv('POSTGRES_PASSWORD'),
                'host': getenv('POSTGRES_HOST'),
                'port': getenv('POSTGRES_PORT'),
                'dbname': getenv('POSTGRES_DB'),
            }
            connection = connect(**connection_conf)
            logger.info('Successfully connected to database')
            return connection
        except Error as e:
            if keep_retrying:
                sleep_secs = backoff * backoff_multiplier
                sleep(sleep_secs)
                return Database._init_connection(connection_conf, keep_retrying, sleep_secs, backoff_multiplier)
            else:
                raise e

    def _open_cursor(self):
        return self.connection.cursor(cursor_factory=RealDictCursor)

    def _execute_query(self, sql, values=None, fetch: Fetch = Fetch.ONE):
        with self._open_cursor() as cursor:
            try:
                cursor.execute(sql, values)
                if fetch == Fetch.NONE:
                    result = None
                elif fetch == Fetch.ONE:
                    result = cursor.fetchone()
                elif fetch == Fetch.ALL:
                    result = cursor.fetchall()
                self.connection.commit()
                return result

            except Error as e:
                logger.exception(f'Failed to execute query "{sql}" with values "{values}"')
                self.connection.rollback()
                raise e

    def update_user(self, uuid, delta) -> RealDictRow:
        sql = '''
            UPDATE users
            SET delta = %(delta)s, updated_at = now()
            WHERE uuid = %(uuid)s
            RETURNING *
        '''
        values = {
            'uuid': uuid,
            'delta': delta
        }
        return self._execute_query(sql, values)
