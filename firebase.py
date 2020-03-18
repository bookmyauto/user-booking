"""
                Description : contains code for firebase handling of user
                Author      : Rahul Tudu
"""
import requests
import config
import logging
import json
import constant as C


class Firebase:

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    #                                                   INITIALIZING WITH A NEW BOOKING                                                                                         #
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    @staticmethod
    def initialize(user_number, fromLon, fromLat, toLon, toLat, booking_id, payment, seats):
        try:
            payload                     = {"driver": C.DRIVER_FREE, "status": C.USER_REQUESTING,
                                           "bookingId": booking_id, "requester": [], "seats": seats, "fare": payment,
                                           "fromLon": float(fromLon), "fromLat": float(fromLat),
                                           "toLon": float(toLon), "toLat": float(toLat), "driverName": C.NO_NAME, "driverVehicle": C.NO_VEHICLE, "driverImage": C.NO_IMAGE}

            payload                     = json.dumps(payload)
            response                    = requests.put(config.FIREBASE_USER + str(user_number) + ".json", data = payload)
            logging.debug("  " + str(user_number) + ":  Put request sent to firebase for initialization")
            if response.status_code == 200:
                return 1
            else:
                logging.debug("  " + str(user_number) + ":  Error in initializing user")
                return 0
        except Exception as e:
            logging.error("  " + str(user_number) + ":  Error while initializing user in firebase users: " + str(e))
            return 0
    
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    #                                                   CHECK STATUS OF USER                                                                                                    #
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    @staticmethod
    def check_user(user_number):
        try:
            response        = requests.get(config.FIREBASE_USER + str(user_number) + ".json")
            if response.status_code == 200:
                response    = dict(response.json())
                return response["driver"], response["status"]
            else:
                logging.debug("  " + str(user_number) + ":  Firebase request status code is " + str(response.status_code))
                return C.WRONG, C.WRONG
        except Exception as e:
            logging.error("  " + str(user_number) + ":  Error while checking firebase database of users: " + str(e))
            return C.WRONG, C.WRONG
    
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    #                                                   CHECK STATUS OF DRIVER                                                                                                  #
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    @staticmethod
    def check_driver(driver_number):
        try:
            response        = requests.get(config.FIREBASE_DRIVER + str(driver_number) + ".json")
            if response.status_code == 200:
                response    = dict(response.json())
                return response["user"], response["status"]
            else:
                return C.WRONG, C.WRONG
        except Exception as e:
            logging.error("  Error while checking firebase database of users: " + str(e))
            return C.WRONG, C.WRONG
    
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    #                                                   RESET USER                                                                                                              #
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    @staticmethod
    def reset_user(user_number):
        try:
            payload                     = {"driver": C.DRIVER_FREE, "status": C.USER_FREE, "bookingId": C.NO_BOOKING,
                                           "seats": C.NO_SEATS, "requester": [], "fare": C.NO_FARE,
                                           "fromLon": C.NO_FROM, "fromLat": C.NO_FROM, "toLon": C.NO_TO,
                                           "toLat": C.NO_TO, "driverName": C.NO_NAME, "driverVehicle": C.NO_VEHICLE, "driverImage": C.NO_IMAGE}

            payload                     = json.dumps(payload)
            response                    = requests.put(config.FIREBASE_USER + str(user_number) + ".json", data = payload)
            if response.status_code == 200:
                return 1
            else:
                logging.debug("  " + str(user_number) + ":  Error in resetting user")
                return 0
        except Exception as e:            
            logging.error("  " + str(user_number) + ":  Error while resetting user in firebase users: " + str(e))
            return 0

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    #                                                   RESET DRIVER                                                                                                            #
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    @staticmethod
    def reset_driver(driver_number):
        try:
            payload                 = {"status": C.DRIVER_FREE, "user": C.USER_FREE, "bookingId": C.NO_BOOKING,
                                       "fare": C.NO_FARE, "seats": C.NO_SEATS, "fromLon": C.NO_FROM,
                                       "fromLat": C.NO_FROM, "toLon": C.NO_TO, "toLat": C.NO_TO}
            payload                 = json.dumps(payload)
            response                = requests.put(config.FIREBASE_DRIVER + str(driver_number) + ".json", data  = payload)
            if response.status_code == 200:
                return 1
            else:
                return 0
        except Exception as e:
            logging.error("  Error while resetting status of driver in firebase drivers: " + str(e))
            return 0

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    #                                                   REQUEST A DRIVER FOR RIDE                                                                                               #
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    @staticmethod
    def request_driver(user_number, driver_number, booking_id, payment, fromLon, fromLat, toLon, toLat, seats):
        try:
            payload                 = {"user": int(user_number), "status": C.DRIVER_GET_REQUEST,
                                       "bookingId": booking_id, "fare": payment, "seats": seats,
                                       "fromLon": float(fromLon), "fromLat": float(fromLat),
                                       "toLon": float(toLon), "toLat": float(toLat)}
            payload                 = json.dumps(payload)
            response                = requests.put(config.FIREBASE_DRIVER + str(driver_number) + ".json", data  = payload)
            if response.status_code == 200:
                return 1
            else:
                return 0
        except Exception as e:
            logging.error("  " + str(user_number) + ":  Error while requesting driver in firebase drivers: " + str(e))
            return 0

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    #                                                   UPDATE REQUESTER LIST OF USER                                                                                           #
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    @staticmethod
    def update_requester(user_number, current_drivers):
        try:
            requester               = {}
            itr                     = 0
            for key, value in current_drivers.items():
                requester[itr]  = int(key)
                itr             = itr + 1
            requester   = json.dumps(requester)
            response    = requests.put(config.FIREBASE_USER + str(user_number) + "/requester.json", data   = requester)
            if response.status_code == 200:
                return 1
            else:
                return 0
        except Exception as e:            
            logging.error("  " + str(user_number) + ":  Error while updating requester of user in firebase users: " + str(e))
            return 0
