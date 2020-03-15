"""
                Description : contains code for database handling
                Author      : Rahul Tudu
"""
import pymysql
import config


class Sql:
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    #                                                   RETURNS INSTANCE OF CURSOR                                                                                              #
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    @staticmethod
    def get_connection():
        conn = pymysql.connect(host=config.HOST, user=config.USER, passwd=config.PASSWORD, db=config.DATABASE)
        cur = conn.cursor()
        return conn, cur
