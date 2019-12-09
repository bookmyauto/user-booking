import requests
import config

class Firebase:
    
    # Checks if any user has a current booking or not
    @staticmethod
    def check_user(user_number):
        try:
            response        = requests.get(config.FIREBASE_USER + user_number + ".json")
            logging.debug("Status code is " + str(response.status_code))
            if response.status_code == 200:
                if response == "null":
                    payload                 = {}
                    payload["driver"]    = 0
                    payload["status"]       = 0
                    payload                 = json.dumps(payload)
                    response                = requests.put(config.FIREBASE_USER + user_number + ".json", data = payload)
                    logging.debug("New user is created in firebase users")
                response    = dict(response.json())
                return response["driver"], response["status"]
            else:
                logging.warning("Firebase request status code is " + str(response.status_code))
                return -1, -1
        except Exception as e:
            logging.error("Error while checking firebase database of users: " + str(e))
            return -1, -1

    # Resets status of a driver
    @staticmethod
    def reset_driver(driver_number):
        try:
            payload             = {}
            payload["status"]   = 0
            payload["user"]     = 0
            response            = requests.put(config.FIREBASE_DRIVER + driver_number + ".json", daata  = payload)
            if response.status_code == 200:
                return 1
            else:
                logging.warning("Firebase request status is " + str(response.status_code))
                return 0
        except Exception as e:
            logging.error("Error while reseting status of driver in firebase drivers")
            return 0

    # Checks status of a driver
    @staticmethod
    def check_driver(driver_number):
        try:
            response        = requests.get(config.FIREBASE_DRIVER + driver_number + ".json")
            logging.debug("Status code is " + str(response.status_code))
            if response.status_code == 200:
                if response == "null":
                    payload             = {}
                    payload["status"]   = 0
                    payload["user"]     = 0
                    payload             = json.dumps(payload)
                    response            = requests.put(config.FIREBASE_DRIVER + driver_number + ".json", data = payload)
                    logging.debug("New driver is created in firebase drivers")
                response    = dict(response.json())
                return response["user"], response["status"]
            else:
                logging.warning("Firebase status code is " + str(response.status_code))
                return -1, -1
        except Exception as e:
            logging.error("Error while checking firebase database of drivers: " + str(e))
            return -1, -1

    # Requests a driver for ride
    @staticmethod
    def request_driver(user_number):
        try:
            payload             = {}
            payload["user"]     = user_number
            payload["status"]   = 1
            response            = requests.put(config.FIREBASE_DRIVER + driver_number + ".json", data  = payload)
            if response.status_code == 200:
                return 1
            else:
                logging.warning("Firebase request status is " + str(response.status_code))
                return 0
        except Exception as e:
            logging.error("Error while requesting driver in firebase drivers")
            return 0

    # Update requester list in firebase
    @staticmethod
    def update_requester(user_number, current_drivers):
        try:
            requester               = []
            for key, value in current_drivers:
                requester.append(key)
            response                = requests.put(config.FIREBASE_USER + user_number + "/requester.json", data   = requester)
            if response.status_code == 200:
                return 1
            else:
                return 0
        except Exception as e:            
            logging.error("Error while updating requester of user in firebase users")
            return 0
