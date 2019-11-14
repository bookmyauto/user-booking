import  logging
from    response import Response
from    bson import ObjectId
from    sql import Sql
from    datetime import datetime


class Book:
    @staticmethod
    def create_booking(user_number, from_latitude, from_longitude, to, cb):
        myconnection    = None
        try:
            myconnection, mycursor  = Sql.get_connection()
            logging.debug("Connection and cursor received")
            sql_query           = "select count(user_number) from user_booking where user_number = '{0}' and current_status = 0"
            mycursor.exeute(sql_query.format(user_number))
            current_booking     = mycursor.fetchone()[0]
            if current_booking == 0:
                now             = datetime.now()
                timestamp       = datetime.timestamp(now)
                booking_id      = str(ObjectId())
                sql_query       = "inser into user_booking(booking_id, user_number, driver_number, timestamp, from_latitude, from_longitude, to_latitude, to_longitude values(%s, %s, %s, %f, %f, %f, %f)"
                val             = (booking_id, user_number, driver_number, timestamp, from_latitude, from_longitude, to_latitude, to_longitude)
                mycursor.exeute(sql_query, val)
                myconnection.commit()
                myconnection.close()
                logging.debug("Booking created successfully for " + str(user_number))
                result = Response.make_result(result_code=201, result_message="Booking created",
                                              display_message="Your booking has been created",
                                              booking_id = booking_id)
                return result
            else:
                myconnection.close()
                logging.debug("Currently booking is going on for " + str(user_number))
                result = Response.make_result(result_code=200, result_message="Booking not created",
                                              display_message="More than one booking is not allowed at a single time",
                                              booking_id=-1)
                return result
        except Exception as e:
            if myconnection is not None:
                myconnection.close()
            logging.error("Error in creating booking: " + str(e) + " |for number: " + str(user_number))
            error = Response.make_error(error_message="system failure", error_code=500,
                                        display_message="Oops something went wrong !")
            return error

    @staticmethod
    def find_nearest_drivers(u_id, latitude, longitude):
        myconnection    = None
        try:
            myconnection, mycursor  = Sql.get_connection()
            logging.debug("Connection and cursor received")
            sql_query       = "select driver_id, driver_latitude, driver_longitude from driver_location where true"
            mycursor.exeute(sql_query)
            data            = mycursor.fetchall()
            driver_vicinity = {}
            for r in data:
                distance                = func(latitude, longitude, r[1], r[2])
                driver_vicinity[r[0]]   = driver_vicinity

        except Exception as e:


    @staticmethod
    def cancel_booking(user_number):
        myconnection    = None
        try:
            myconnection, mycursor  = Sql.get_connection()
            logging.debug("Connection and cursor received")
            sql_query   = "update user_booking set status = %s where user_number = %s and current_status = %d"
            val         = ("user_cancelled", user_number, 1)
            mycursor.exeute(sql_query, val)
            myconnection.commit()
            myconnection.close()
            logging.debug("Booking cancelled successfully for " + str(user_number))
            result = Response.make_result(result_code=200, result_message="Booking cancelled",
                                          display_message="Your booking has been cancelled")
            return result
        except Exception as e:
            if myconnection is not None:
                myconnection.close()
            logging.error("Error in cancelling booking: " + str(e) + " |for number: " + str(user_number))
            error = Response.make_error(error_message="system failure", error_code=500,
                                        display_message="Oops something went wrong !")
            return error
