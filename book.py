"""
                Description : contains code for booking
                Author      : Rahul Tudu
"""
import  logging
from    bson        import ObjectId
from    datetime    import datetime
import  constant    as C

from    sql         import Sql
from    firebase    import Firebase
from    response    import Response
from    fare        import Fare
from    utility     import Utility


class Book:

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    #                                                                   RESETTING EVERYTHING BEFORE CLOSING                                                                     #
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    @staticmethod
    def closure_reset(current_drivers, user_number):
        conn = None
        try:
            conn, cur       = Sql.get_connection()
            logging.debug("  " + str(user_number) + ":  Got connection in closure reset")
            for key, value in current_drivers.items():
                _           = Firebase.reset_driver(key)
                sql_query   = "update driver_status set status = {0} where driver_number = '{1}'"
                cur.execute(sql_query.format(C.DRIVER_FREE, key))
                conn.commit()
            _               = Firebase.reset_user(user_number)
            logging.debug("  " + str(user_number) + ":  User reset done")
            _               = Firebase.update_requester(user_number, {})
            logging.debug("  " + str(user_number) + ":  Requester reset done")
            conn.close()
        except Exception as e:
            if conn is not None:
                conn.close()
            logging.error("  " + str(user_number) + ":  Error in closure: " + str(e))

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    #                                                                   RETURNS FARE                                                                                            #
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    @staticmethod
    def get_fare(from_lon, from_lat, to_lon, to_lat):
        conn = None
        try:
            payment     = 10
            result      = Response.make_response(200, "", "", fare=payment)
            return result
        except Exception as e:
            if conn is not None:
                conn.close()
            logging.debug("  Error in returning fare: " + str(e))
            return Response.default_error

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    #                                                                   CREATE BOOKING                                                                                          #
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    @staticmethod
    def create_booking(user_number, from_lon, from_lat, to_lon, to_lat, seats):
        conn            = None
        max_queue_size  = 2
        current_drivers = {}
        try:
            conn, cur = Sql.get_connection()
            logging.debug("  " + str(user_number) + ":  Connection and cursor received")

            # Get payment details
            payment         = Fare.get_fare(from_lat, from_lon, to_lat, to_lon)
            if payment == -1:
                conn.close()
            seats           = int(seats)
            booking_id      = str(ObjectId())
            sql_query       = "select driver_number, curr_lat, curr_long from driver_status where status = 6"
            cur.execute(sql_query)
            data            = cur.fetchall()
            data, status    = Utility.sort_drivers(from_lat, from_lon, data)
            logging.debug("  " + str(user_number) + ":  Drivers sorted according to distance")
            if status == 0:
                conn.close()
            now_time        = datetime.timestamp(datetime.now())
            end_time        = now_time + 60
            driver_index    = 0
            driver_number   = -1
            status          = Firebase.initialize(user_number, from_lon, from_lat, to_lon, to_lat, booking_id, payment, seats)
            logging.debug("  " + str(user_number) + ":  Firebase user initialized")
            if status == 0:
                Book.closure_reset(current_drivers, user_number)
                conn.close()

            # Try for 60 seconds requesting drivers
            logging.info("  " + str(user_number) + ":  60 seconds booking search started")
            while now_time <= end_time:
                driver_number, status   = Firebase.check_user(user_number)
                if status == C.WRONG:
                    conn.close()
                    Book.closure_reset(current_drivers, user_number)
                if status == C.USER_BOOKED or status == C.USER_IN_RIDE:

                    # Flush list of current drivers
                    for key, value in current_drivers.items():
                        _   = Firebase.reset_driver(key)

                    # Flush requester list of user
                    _   = Firebase.update_requester(user_number, {})
                    break

                # Check if driver has cancelled any request
                to_remove   = []
                for key, value in current_drivers.items():
                    user, status = Firebase.check_driver(key)
                    if status == C.DRIVER_FREE:
                        if key in current_drivers:
                            to_remove.append(key)
                for key in to_remove:
                    del current_drivers[key]

                # Send request to new driver
                while driver_index < len(data):
                    if len(current_drivers) == max_queue_size:
                        break
                    driver_number   = data[driver_index][0]
                    logging.debug("  " + str(user_number) + ":  Sending request to driver " + str(driver_number))
                    status          = Firebase.request_driver(user_number, driver_number, booking_id, payment, from_lon,
                                                              from_lat, to_lon, to_lat, seats)
                    if status == 0:
                        driver_index = driver_index + 1
                        continue
                    current_drivers[driver_number]  = 1
                    driver_index                    = driver_index + 1

                # Update requester list of user
                logging.debug("  " + str(user_number) + ": Updating requester")
                _           = Firebase.update_requester(user_number, current_drivers)
                now_time    = datetime.timestamp(datetime.now())

            # Return result
            if int(driver_number) != C.DRIVER_FREE:
                logging.debug("  " + str(user_number) + ":  Create booking function ended")
                conn.close()
            else:
                logging.debug("  " + str(user_number) + ":  Create booking function ended")
                Book.closure_reset(current_drivers, user_number)
                conn.close()
        except Exception as e:
            Book.closure_reset(current_drivers, user_number)
            if conn is not None:
                conn.close()
            logging.error("  " + str(user_number) + ":  Error in create booking: " + str(e))

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    #                                                                   FINDING DRIVERS                                                                                         #
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    @staticmethod
    def find_drivers(user_number, from_lon, from_lat, to_lon, to_lat, seats):
        conn = None
        try:
            conn, cur       = Sql.get_connection()
            logging.debug("  " + str(user_number) + ":  Connection and cursor received")
            sql_query       = "select count(booking_id) from user_booking where user_number = '{0}' and (status = {1} or status = {2} or status = {3})"
            cur.execute(sql_query.format(user_number, C.USER_IN_RIDE, C.USER_BOOKED, C.USER_REQUESTING))
            current_booking = cur.fetchone()[0]
            # if already there is no booking then proceed
            if current_booking == 0:
                conn.close()
                path_ = "users/" + user_number
                result = Response.make_response(200, "Success", "We are searching drivers", path=path_)
                return result, 1
            else:
                conn.close()
                result = Response.make_response(409, "Booking exists", "You have already one booking going on")
                return result, 0

        except Exception as e:
            if conn is not None:
                conn.close()
            logging.error("  " + str(user_number) + ":  Error in finding drivers: " + str(e))
            return Response.default_error, 0

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    #                                                                   CANCEL BOOKING                                                                                          #
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    @staticmethod
    def cancel_booking(user_number, booking_id):
        conn = None
        try:
            conn, cur = Sql.get_connection()
            logging.debug("  " + str(user_number) + ":  Connection and cursor received")
            status = Firebase.reset_user(user_number)
            if status == 0:
                return Response.default_error

            sql_query = "update user_booking set status = {0}, activity = concat(activity, '|', 'user_cancelled') where booking_id = '{1}' and status != {2}"
            cur.execute(sql_query.format(C.USER_CANCELLED, booking_id, C.USER_CANCELLED))
            conn.commit()

            sql_query = "update distance set status = 0 where booking_id = '{0}'"
            cur.execute(sql_query.format(booking_id))
            conn.commit()

            conn.close()
            logging.debug("Booking cancelled successfully for " + str(user_number))
            result = Response.make_response(200, "Booking cancelled", "Your booking has been cancelled")
            return result
        except Exception as e:
            if conn is not None:
                conn.close()
            logging.error("  " + str(user_number) + ":  Error in cancelling booking: " + str(e))
            return Response.default_error

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    #                                                                   END TRIP                                                                                                #
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    @staticmethod
    def end_trip(user_number, booking_id):
        conn = None
        try:
            conn, cur = Sql.get_connection()
            logging.debug("  " + str(user_number) + ":  Connection and cursor received")
            status = Firebase.reset_user(user_number)
            logging.debug("  " + str(user_number) + ":  User reset done")
            if status == 0:
                raise ValueError("Error in ending trip")

            sql_query = "update user_booking set activity = concat(activity, '|', 'user_end_trip'), status = {0} where booking_id = '{1}' and status != {2}"
            cur.execute(sql_query.format(C.USER_END_TRIP, booking_id, C.USER_END_TRIP))
            conn.commit()

            conn.close()
            result = Response.make_response(200, "Ended", "Trip ended")
            return result
        except Exception as e:
            if conn is not None:
                conn.close()
            logging.error("  " + str(user_number) + ":  Error in end trip request: " + str(e))
            return Response.default_error

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    #                                                                   GETTING DISTANCE                                                                                         #
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    @staticmethod
    def get_dist(user_number, curr_lon, curr_lat, driver_nummber):
        conn = None
        try:
            conn, cur = Sql.get_connection()
            logging.debug("  " + str(user_number) + ":  Connection and cursor received")
            sql_query = "select curr_lon, curr_lat from driver_status where  driver = '{0}'"
            cur.execute(sql_query.format(driver_nummber))
            driver_lon  = cur.fetchone()[0]
            driver_lat  = cur.fetchone()[1]
            dist        = driver_lon + driver_lat - curr_lon - curr_lat
            result      = Response.make_response(200, "", "", distance = dist)
            return result
        except Exception as e:
            if conn is not None:
                conn.close()
            logging.error("  " + str(user_number) + ":  Error in getting current distance: " + str(e))
            return Response.default_error
