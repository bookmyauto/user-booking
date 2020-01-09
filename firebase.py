import requests
import config
import logging
import json
import constant as C

class Firebase:
    
    # Checks if any user has a current booking or not
    @staticmethod
    def check_user(user_number, from_lon, from_lat, to_lon, to_lat, booking_id, paymemt):
        try:
            response        = requests.get(config.FIREBASE_USER + user_number + ".json")
            logging.debug("Status code is " + str(response.status_code))
            if response.status_code == 200:
                if response.json() is None:
                    payload                 = {}
                    payload["requester"]    = []
                    payload["driver"]       = C.DRIVER_FREE
                    payload["status"]       = C.USER_FREE
                    payload["bookingId"]    = booking_id
                    payload["from_lon"]     = from_lon
                    payload["from_lat"]     = from_lat
                    payload["to_lon"]       = to_lon
                    payload["to_lat"]       = to_lat
                    payload["fare"]         = payment

                    payload                 = json.dumps(payload)
                    response                = requests.put(config.FIREBASE_USER + user_number + ".json", data = payload)
                    logging.debug("New user is created in firebase users")
                response    = dict(response.json())
                return response["driver"], response["status"]
            else:
                logging.warning("Firebase request status code is " + str(response.status_code))
                return C.WRONG, C.WRONG
        except Exception as e:
            logging.error("Error while checking firebase database of users: " + str(e))
            return C.WRONG, C.WRONG

    # Resets status of a user
    @staticmethod
    def reset_user(user_number):
        try:
            payload                     = {}
            payload["driver"]           = C.DRIVER_FREE
            payload["status"]           = C.USER_FREEE
            payload["bookingId"]        = C.NO_BOOKING
            payload["requester"]        = []
            payload["fare"]             = C.NO_FARE
            payload["from_lon"]         = C.NO_FROM
            payload["from_lat"]         = C.NO_FROM
            payload["to_lon"]           = C.NO_TO
            payload["to_lat"]           = C.NO_TO

            payload                     = json.dumps(payload)
            response                    = requests.put(config.FIREBASE_USER + user_number + ".json", data = payload)
            if response.status_code == 200:
                return 1
            else:
                logging.debug("Error in resetting user")
                return 0
        except Exception as e:            
            logging.error("Error while resetting user in firebase users: " + str(e))
            return 0

    # Resets status of a driver
    @staticmethod
    def reset_driver(driver_number):
        try:
            payload                 = {}
            payload["status"]       = C.DRIVER_FREE
            payload["user"]         = C.USER_FREE
            payload["bookingId"]    = C.NO_BOOKING
            payload["fare"]         = C.NO_FARE
            payload["from_lon"]     = C.NO_FROM
            payload["from_lat"]     = C.NO_FROM
            payload["to_lon"]       = C.NO_TO
            payload["to_lat"]       = C.NO_TO
            payload                 = json.dumps(payload)
            response                = requests.put(config.FIREBASE_DRIVER + driver_number + ".json", data  = payload)
            if response.status_code == 200:
                return 1
            else:
                logging.warning("Firebase request status is " + str(response.status_code))
                return 0
        except Exception as e:
            logging.error("Error while resetting status of driver in firebase drivers: " + str(e))
            return 0

    # Checks status of a driver
    @staticmethod
    def check_driver(driver_number):
        try:
            response        = requests.get(config.FIREBASE_DRIVER + driver_number + ".json")
            logging.debug("Status code is " + str(response.status_code))
            if response.status_code == 200:
                response    = dict(response.json())
                return response["user"], response["status"]
            else:
                logging.warning("Firebase status code is " + str(response.status_code))
                return C.WRONG, C.WRONG
        except Exception as e:
            logging.error("Error while checking firebase database of drivers: " + str(e))
            return C.WRONG, C.WRONG

    # Requests a driver for ride
    @staticmethod
    def request_driver(user_number, driver_number, booking_id, payment, from_, to_):
        try:
            payload                 = {}
            payload["user"]         = user_number
            payload["status"]       = C.DRIVER_GET_REQUEST
            payload["bookingId"]    = booking_id
            payload["fare"]         = payment
            payload["from_lon"]     = from_lon
            payload["from_lat"]     = from_lat
            payload["to_lon"]       = to_lon
            payload["to_lat"]       = to_lat
            payload                 = json.dumps(payload)
            response                = requests.put(config.FIREBASE_DRIVER + driver_number + ".json", data  = payload)
            if response.status_code == 200:
                return 1
            else:
                logging.warning("Firebase request status is " + str(response.status_code))
                return 0
        except Exception as e:
            logging.error("Error while requesting driver in firebase drivers: " + str(e))
            return 0

    # Update requester list in firebase
    @staticmethod
    def update_requester(user_number, current_drivers):
        try:
            requester               = {}
            itr                     = 0
            for key, value in current_drivers.items():
                requester[itr]  = key
                itr             = itr + 1
            requester   = json.dumps(requester)
            response    =  requests.put(config.FIREBASE_USER + user_number + "/requester.json", data   = requester)
            if response.status_code == 200:
                return 1
            else:
                return 0
        except Exception as e:            
            logging.error("Error while updating requester of user in firebase users: " + str(e))
            return 0

    # Cancel booking of an user
    @staticmethod
    def cancel_booking(user_number):
        try:
            response                    = requests.get(config.FIREBASE_USER + user_number + ".json")
            current_driver              = -1
            if response.status_code == 200:
                response                = dict(response.json())
                current_driver          = str(response["driver"])
                payload                 = {}
                payload["user"]         = C.USER_FREE
                payload["status"]       = C.DRIVER_FREE
                payload["bookingId"]    = C.NO_BOOKING
                payload["fare"]         = C.NO_FARE
                payload["from_lon"]     = C.NO_FROM
                payload["from_lat"]     = C.NO_FROM
                payload["to_lon"]       = C.NO_TO
                payload["to_lat"]       = C.NO_TO

                payload                 = json.dumps(payload)
                response                = requests.put(config.FIREBASE_DRIVER + current_driver + ".json", data = payload)
                if response.status_code != 200:
                    return 0
            else:
                return 0
            payload                     = {}
            payload["driver"]           = C.DRIVER_FREE
            payload["status"]           = C.USER_FREE
            payload["requester"]        = []
            payload["bookingId"]        = C.NO_BOOKING
            payload["fare"]             = C.NO_FARE
            payload["from_lon"]         = C.NO_FROM
            payload["from_lat"]         = C.NO_FROM
            payload["to_lon"]           = C.NO_TO
            payload["to_lat"]           = C.NO_TO
            payload                     = json.dumps(payload)
            response                    = requests.put(config.FIREBASE_USER + user_number + ".json", data = payload)
            if response.status_code == 200:
                return current_driver, 1
            else:
                logging.debug("Error in cancelling booking")
                return -1, 0
        except Exception as e:            
            logging.error("Error while cancelling booking of user in firebase users: " + str(e))
            return -1, 0
