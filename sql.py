import psycopg2
import config


class Sql:

    # returns instance of cursor
    @staticmethod
    def get_connection():
        conn = psycopg2.connect(database=config.database, user=config.user, password=config.password,
                                host=config.host, port="5432")
        mycursor = conn.cursor()
        return conn, mycursor
