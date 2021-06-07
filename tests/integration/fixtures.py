from server.src.database import Database, Fetch


class Fixtures(Database):
    def __init__(self, connection=None, connection_conf=None):
        connection_conf = connection_conf or {
            'user': 'iiot',
            'password': 'lorem',
            'host': 'localhost',
            'port': '5432',
            'dbname': 'iiot',
        }
        super().__init__(connection, connection_conf)

    def clean_database(self):
        self._execute_query("TRUNCATE TABLE users", fetch=Fetch.NONE)

    def close_connection(self):
        self.connection.close()
