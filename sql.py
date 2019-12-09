import pymysql
import config

class Sql:
    
    # returns instance of cursor
    @staticmethod
    def get_connection():
        conn = pymysql.connect(host=config.host, user=config.user, passwd=config.password, db=config.database)
        cur = conn.cursor()
        return conn, cur
