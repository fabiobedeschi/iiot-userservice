from enum import Enum
from logging import getLogger
from os import getenv
from typing import List

from psycopg2 import connect, Error
from psycopg2.extras import RealDictCursor, RealDictRow

logger = getLogger()


class Fetch(Enum):
    NONE = 0
    ONE = 1
    ALL = -1


class Database:
    def __init__(self, connection=None, connection_conf=None):
        self.connection = connection or Database._init_connection(connection_conf)

    @staticmethod
    def _init_connection(connection_conf):
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

    def find_all_users(self) -> List[RealDictRow]:
        sql = '''
            SELECT * FROM users
        '''
        return self._execute_query(sql, fetch=Fetch.ALL)

    def find_user(self, uuid) -> RealDictRow:
        sql = '''
            SELECT * FROM users
            WHERE uuid = %(uuid)s
        '''
        values = {'uuid': uuid}
        return self._execute_query(sql, values)

    def find_users_by_area(self, area) -> List[RealDictRow]:
        sql = '''
            SELECT * FROM users
            WHERE area = %(area)s
        '''
        values = {'area': area}
        return self._execute_query(sql, values, fetch=Fetch.ALL)

    def update_user(self, uuid, delta=None, area=None) -> RealDictRow:
        sql = 'UPDATE users SET updated_at = NOW() '
        if area is not None:
            sql += ', area = %(area)s '
        if delta is not None:
            sql += ', delta = %(delta)s '
        sql += 'WHERE uuid = %(uuid)s '
        sql += '''
            RETURNING *, (
                SELECT area FROM users WHERE uuid = %(uuid)s
            ) AS old_area
        '''
        values = {
            'uuid': uuid,
            'delta': delta,
            'area': area
        }
        return self._execute_query(sql, values)

    def insert_user(self, uuid, delta=None, area=None) -> RealDictRow:
        delta = delta or 0
        area = area or ''
        sql = '''
            INSERT INTO users(uuid, delta, area)
            VALUES (%(uuid)s, %(delta)s, %(area)s)
            RETURNING *
        '''
        values = {
            'uuid': uuid,
            'delta': delta,
            'area': area
        }
        return self._execute_query(sql, values)

    def delete_user(self, uuid) -> RealDictRow:
        sql = '''
            DELETE FROM users
            WHERE uuid = %(uuid)s
            RETURNING *
        '''
        values = {'uuid': uuid}
        return self._execute_query(sql, values)
