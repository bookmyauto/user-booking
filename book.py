import  logging
from    bson        import ObjectId
from    datetime    import datetime

import  config
import  constant    as C

from    sql         import Sql
from    firebase    import Firebase
from    response    import Response
from    fare        import Fare
from    utility     import Utility

class Book:

    @staticmethod
    def closure_reset(current_drivers, user_number):
        conn            = None
        try:
            conn, cur   = Sql.get_connection()
            for key, value in current_drivers.items():
                status      = Firebase.reset_driver(key)
                sql_query   = "update driver_status set status = {0} where driver_number = '{1}'"
                cur.execute(sql_query.format(C.DRIVER_FREE, key))
                conn.commit()
            status      = Firebase.reset_user(user_number)
            status      = Firebase.update_requester(user_number, {})
            conn.close()
        except Exception as e:
            if conn is not None:
                conn.close()
            logging.error("Error in closure: " + str(e))
        

    @staticmethod
    def create_booking(user_number, from_lon, from_lat, to_lon, to_lat):
        conn                        = None
        max_queue_size              = 2
        current_drivers             = {}
        try:
            conn, cur               = Sql.get_connection()
            logging.debug("Connection and cursor received")
            sql_query               = "select count(booking_id) from user_booking where user_number = '{0}' and (status = {1} or status = {2})"
            cur.execute(sql_query.format(user_number, C.USER_IN_RIDE, C.USER_BOOKED))
            current_booking         = cur.fetchone()[0]
            if current_booking == 0:
                
                # Get payment details
                payment             = Fare.get_fare(from_latitude, from_longitude, to_latitude, to_longitude)
                if payment == -1:
                    conn.close()
                    return Response.default_error

                booking_id          = str(ObjectId())
                sql_query           = "select driver_number, curr_lat, curr_long from driver_status where status = {0}"
                cur.execute(sql_query.format(C.DRIVER_FREE))
                data                = cur.fetchall()
                data, status        = Utility.sort_drivers(from_latitude, from_longitude, data)
                if(status == 0):
                    conn.close()
                    return Response.default_error
                now_time            = datetime.timestamp(datetime.now())
                end_time            = now_time + 60
                driver_index        = 0
                driver_number       = -1
                driver_number, status   = Firebase.check_user(user_number, from_lon, from_lat, to_lon, to_lat, bookcing_id, payment)
                while now_time <= end_time:
                    driver_number, status   = Firebase.check_user(user_number)
                    if status == C.WRONG:
                        conn.close()
                        closure_reset(current_drivers, user_number)
                        return Response.default_error
                    if status == C.USER_BOOKED or status == C.USER_IN_RIDE: 
                        # Flush list of current drivers
                        for key, value in current_drivers.items():
                            if int(key) != int(driver_number):
                                status  = Firebase.reset_driver(key)
                        # Flush requester list of user
                        status  = Firebase.update_requester(user_number, {})
                        break

                    # Check if driver has cancelled any request
                    to_remove   = []
                    for key, value in current_drivers.items():
                        user, status  = Firebase.check_driver(key)
                        if status == C.DRIVER_FREE:
                            if key in current_drivers:
                                to_remove.append(key)
                    for key in to_remove:
                        del current_drivers[key]

                    # Send request to new driver
                    while driver_index < len(data):
                        if(len(current_drivers) == 2):
                            break
                        driver_number                   = data[driver_index][0]
                        status                          = Firebase.request_driver(user_number, driver_number, booking_id, payment, from_lon, from_lat, to_lon, to_lat)
                        if status == 0:
                            driver_index                = driver_index + 1
                            continue
                        current_drivers[driver_number]  = 1
                        sql_query                       = "update driver_status set status = {0} where driver_number = '{1}'"
                        cur.execute(sql_query.format(C.DRIVER_GET_REQUEST, driver_number))
                        conn.commit()
                        driver_index                    = driver_index + 1
                    
                    # Update requester list of user
                    status      = Firebase.update_requester(user_number, current_drivers)
                    now_time    = datetime.timestamp(datetime.now())


                # Return result
                if int(driver_number) > 0:
                    for key, value in current_drivers.items():
                        if int(key) != int(driver_number):
                            status  = Firebase.reset_driver(key)
                    status      = Firebase.update_requester(user_number, {})
                    conn.close()
                    result = Response.make_result(200, "Got driver", "", fare = payment, gotDriver = 1, driverNumber = driver_number, bookingId = booking_id)
                    return result
                else:
                    closure_reset(current_drivers, user_number)
                    conn.close()
                    result  = Response.make_result(200, "Did not get driver", "Sorry all our drivers are busy", fare = 0, gotDriver = 0, driverNumber = driver_number)
                    return result
        except Exception as e:
            closure_reset(current_drivers, user_number)
            if conn is not None:
                conn.close()
            logging.error("Error in create booking: " + str(e))
            return Response.default_error

    @staticmethod
    def cancel_booking(user_number, booking_id):
        conn    = None
        try:
            conn, cur   = Sql.get_connection()
            logging.debug("Connection and cursor received")
            driver_number, status      = Firebase.cancel_booking(user_number)
            if status == 0:
                return Response.default_error

            sql_query   = "select activity from user_booking where booking_id = '{0}'"
            cur.execute(sql_query.format(booking_id))
            activity    = curr.fetchone()[0]
            activity    = activity + "user_cancelled|"
            
            sql_query   = "update user_booking set status = {0} and activity = '{1}' where booking_id = '{2}'"
            cur.exeute(sql_query.format(C.USER_CANCELLED, activity, booking_id))
            conn.commit()

            sql_query   = "update driver_status set status = {0} where driver_number = '{1}'"
            cur.execute(sql_query.format(C.DRIVER_FREE, driver_number))
            conn.commit()
            conn.close()
            logging.debug("Booking cancelled successfully for " + str(user_number))
            result = Response.make_result(200, "Booking cancelled", "Your booking has been cancelled")
            return result
        except Exception as e:
            if conn is not None:
                conn.close()
            logging.error("Error in cancelling booking: " + str(e))
            return Response.default_error
