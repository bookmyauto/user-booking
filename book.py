import  logging
from    bson        import ObjectId

import  config
import  constant

from    sql         import Sql
from    datetime    import datetime
from    firebase    import Firebase
from    response    import Response
from    fare        import Fare

class Book:
    
    @staticmethod
    def create_booking(user_number, from_latitude, from_longitude, to_latitude, to_longitude):
        conn                        = None
        max_queue_size              = 2
        try:
            conn, cur               = Sql.get_connection()
            logging.debug("Connection and cursor received")
            sql_query               = "select count(number) from user_booking where user_number = '{0}' and status = 1"
            cur.exeute(sql_query.format(user_number))
            current_booking         = cur.fetchone()[0]
            if current_booking == 0:
                booking_id          = str(ObjectId())
                sql_query           = "select driver_number, curr_lat, curr_long from driver_status where status = 0"
                data                = cur.fetchall()
                data, status        = sort_drivers(from_latitude, from_longitude, data)
                if(status == 0):
                    error = Response.make_error(error_code = 500, error_message = "System failure", display_message = "Oops something went wrong !")
                    conn.close()
                    return error
                now_time            = datetime.timestamp(datetime.now())
                end_time            = now_time + 60
                driver_index        = 0
                current_drivers     = {}
                driver_number           = -1
                while now_time <= end_time:
                    driver_number, status       = Firebase.check_user(user_number)
                    if status == 1:
                        
                        # Flush list of current drivers
                        for key, value in current_drivers.items():
                            if key != driver_number:
                                status  = Firebase.reset_driver(key)
                        break

                    # Check if driver has cancelled any request
                    for key, value in current_drivers.items():
                        status  = Firebase.check_driver(key)
                        if status == 0:
                            del current_drivers[key]

                    # Send request to new driver
                    while driver_index < len(data):
                        driver_number                   = data[driver_index][0]
                        status                          = Firebase.request_driver(user_number, driver_number)
                        if status == 0:
                            driver_index                = driver_index + 1
                            continue
                        current_drivers[driver_number]  = 1
                        driver_index                    = driver_index + 1
                        if(len(curr_drivers) == 2):
                            break
                    
                    # Update requester list if user
                    status      = Firebase.update_requester(user_number, current_drivers)
                    now_time    = datetime.timestamp(datetime.now())

                # Get payment details
                payment = Fare.get_fare(from_latitude, from_longitude, to_latitude, to_longitude)
                if payment == -1:
                    conn.close()
                    error = Response.make_error(error_message = "System failure", error_code = 500, display_message = "Oops something went wrong !")
                    return error

                # Return result
                if driver_number > 0:
                    sql_query   = "insert user_booking(booking_id, user_number, status, driver_number, fare) values('{0}', '{1}', 1, '{2}', {3})"
                    cur.execute(sql_query.format(booking_id, user_number, driver_number, payment))
                    conn.commit()
                    conn.close()
                    result = Response.make_result(result_code = 200, result_message = "Got driver", display_message = "", fare = payment, got_driver = 1, driver_number = driver_number)
                    return result
                else:
                    conn.close()
                    result = Response.make_result(result_code = 200, result_message = "Did not get driver", display_message = "Sorry all our drivers are busy", fare = 0, got_driver = 0, driver_number = driver_number)
                    return result
        except Exception as e:
            if conn is not None:
                conn.close()
            logging.error("Error in creating booking: " + str(e))
            error = Response.make_error(error_message = "System failure", error_code = 500, display_message = "Oops something went wrong !")
            return error

    @staticmethod
    def sort_drivers(curr_lat, curr_long, data):
        try:
            driver_distance = []
            for row in data:
                driver_id   = row[0]
                lat         = row[1]
                lon         = row[2]
                dist        = distance(lat, lon,  curr_lat, curr_lon)
                driver_distance.extend([[driver_id, dist]])
            driver_distance.sort(key = lambda x: x[1])
            return driver_distance, 1
        except Exception as e:
            return [], 0


    @staticmethod
    def cancel_booking(user_number):
        conn    = None
        try:
            conn, cur   = Sql.get_connection()
            logging.debug("Connection and cursor received")
            sql_query   = "update user_booking set status = {0} where user_number = '{1}' and status = {2}"
            cur.exeute(sql_query.format(constant.USER_CANCELLED, user_number, constant.BOOKING_DONE))
            conn.commit()
            conn.close()
            logging.debug("Booking cancelled successfully for " + str(user_number))
            result = Response.make_result(result_code = 200, result_message = "Booking cancelled", display_message = "Your booking has been cancelled")
            return result
        except Exception as e:
            if conn is not None:
                conn.close()
            logging.error("Error in cancelling booking: " + str(e))
            error = Response.make_error(error_message = "System failure", error_code = 500, display_message = "Oops something went wrong !")
            return error
