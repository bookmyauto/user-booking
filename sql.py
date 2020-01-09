import pymysql
import config

class Sql:
    
    # returns instance of cursor
    @staticmethod
    def get_connection():
        conn = pymysql.connect(host=config.HOST, user=config.USER, passwd=config.PASSWORD, db=config.DATABASE)
        cur = conn.cursor()
        return conn, cur
