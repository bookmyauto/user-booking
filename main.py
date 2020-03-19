"""
                Description : main file for user booking service
                Author      : Rahul Tudu
"""
import logging
import threading
import json
from flask import make_response
from flask import Flask
from flask import request
from book import Book
from authorize import Authorize

# --------------------------------------------------------------------------------------------------------------------------------------------- #
#                                                       INITIALIZATION                                                                          #
# --------------------------------------------------------------------------------------------------------------------------------------------- #
logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
default_error = json.dumps(
    {"errorCode": 500, "errorMessage": "System failure", "displayMessage": "Oops something went wrong !"})
token_expiry_error = json.dumps(
    {"errorCode": 401, "errorMessage": "Token expired", "displayMessage": "Login again, session expired"})
with app.app_context():
    default_error = make_response(default_error)
with app.app_context():
    token_expiry_error = make_response(token_expiry_error)
logging.info("user booking started")


# --------------------------------------------------------------------------------------------------------------------------------------------- #
#                                                       CHECK IF WORKING                                                                        #
# --------------------------------------------------------------------------------------------------------------------------------------------- #
@app.route("/v1")
def working():
    return "user-booking service running"


# --------------------------------------------------------------------------------------------------------------------------------------------- #
#                                                       USER RIDE BOOKING                                                                       #
# --------------------------------------------------------------------------------------------------------------------------------------------- #
@app.route("/v1/book", methods=["POST"])
def book():
    try:
        if request.method == "POST":
            jwt_token               = request.headers["token"]
            stat, tok               = Authorize.verify_jwt(jwt_token)
            if stat == 0:
                raise ValueError("Not authorized")
            if len(tok) > 0:
                logging.critical("failure in v1/book with token expired: ")
                return token_expiry_error

            if "fromLatitude" in request.form:
                user_number         = request.form["number"]
                from_latitude       = request.form["fromLatitude"]
                from_longitude      = request.form["fromLongitude"]
                to_latitude         = request.form["toLatitude"]
                to_longitude        = request.form["toLongitude"]
                seats               = request.form["seats"]
                response, s         = Book.find_drivers(user_number, from_longitude, from_latitude, to_longitude, to_latitude, seats)
                response            = json.dumps(response)
                if s == 1:
                    t               = threading.Thread(name="create booking", target=Book.create_booking, args=(
                                        user_number, from_longitude, from_latitude, to_longitude, to_latitude, seats,))
                    t.setDaemon(True)
                    t.start()
                with app.app_context():
                    response        = make_response(response)
                return response
    except RuntimeError as e:
        logging.critical("failure in v1/book with error: " + str(e))
        return default_error


# --------------------------------------------------------------------------------------------------------------------------------------------- #
#                                                       CANCEL A BOOKING                                                                        #
# --------------------------------------------------------------------------------------------------------------------------------------------- #
@app.route("/v1/cancel", methods=["POST"])
def cancel():
    try:
        if request.method == "POST":
            jwt_token               = request.headers["token"]
            stat, tok               = Authorize.verify_jwt(jwt_token)
            if stat == 0:
                raise ValueError("Not authorized")
            if len(tok) > 0:
                logging.critical("failure in v1/cancel with token expired: ")
                return token_expiry_error
            user_number             = request.form["number"]
            booking_id              = request.form["bookingId"]
            response                = Book.cancel_booking(user_number, booking_id)
            response                = json.dumps(response)
            with app.app_context():
                response            = make_response(response)
            return response
    except RuntimeError as e:
        logging.critical("failure in v1/cancel with error: " + str(e))
        return default_error

# --------------------------------------------------------------------------------------------------------------------------------------------- #
#                                                       GET FARE                                                                                #
# --------------------------------------------------------------------------------------------------------------------------------------------- #
@app.route("/v1/fare", methods=["GET"])
def fare():
    try:
        if request.method == "GET":
            jwt_token               = request.headers["token"]
            stat, tok               = Authorize.verify_jwt(jwt_token)
            if stat == 0:
                raise ValueError("Not authorized")
            if len(tok) > 0:
                logging.critical("failure in v1/fare with token expired: ")
                return token_expiry_error
            user_number             = request.args["number"]
            from_latitude           = request.args["fromLatitude"]
            from_longitude          = request.args["fromLongitude"]
            to_latitude             = request.args["toLatitude"]
            to_longitude            = request.args["toLongitude"]
            response                = Book.get_fare(from_longitude, from_latitude, to_longitude, to_latitude)
            response                = json.dumps(response)
            with app.app_context():
                response            = make_response(response)
            return response
    except RuntimeError as e:
        logging.critical("failure in v1/fare with error: " + str(e))
        return default_error

# --------------------------------------------------------------------------------------------------------------------------------------------- #
#                                                       ENDING TRIP                                                                             #
# --------------------------------------------------------------------------------------------------------------------------------------------- #
@app.route("/v1/endTrip", methods=["POST"])
def end_trip():
    try:
        if request.method == "POST":
            jwt_token               = request.headers["token"]
            stat, tok               = Authorize.verify_jwt(jwt_token)
            if stat == 0:
                raise ValueError("Not authorized")
            if len(tok) > 0:
                logging.critical("failure in v1/endTrip with token expired: ")
                return token_expiry_error
            user_number             = request.form["number"]
            booking_id              = request.form["bookingId"]
            response                = Book.end_trip(user_number, booking_id)
            response                = json.dumps(response)
            with app.app_context():
                response            = make_response(response)
            return response
    except RuntimeError as e:
        logging.critical("failure in v1/endTrip with error: " + str(e))
        return default_error


# --------------------------------------------------------------------------------------------------------------------------------------------- #
#                                                       GETS DISTANCE                                                                           #
# --------------------------------------------------------------------------------------------------------------------------------------------- #
@app.route("/v1/getDistance", methods=["GET"])
def get_distance():
    try:
        if request.method == "GET":
            jwt_token               = request.headers["token"]
            stat, tok               = Authorize.verify_jwt(jwt_token)
            if stat == 0:
                raise ValueError("Not authorized")
            if len(tok) > 0:
                logging.critical("failure in v1/getDistance with token expired: ")
                return token_expiry_error
            user_number             = request.args["number"]
            driver_number           = request.args["driver"]
            curr_lon                = request.args["currLongitude"]
            curr_lat                = request.args["currLatitude"]
            response                = Book.get_dist(user_number, curr_lon, curr_lat, driver_number)
            response                = json.dumps(response)
            response                = make_response(response)

            return response
    except RuntimeError as e:
        logging.critical("failure in v1/getDistance with error: " + str(e))
        return default_error


# --------------------------------------------------------------------------------------------------------------------------------------------- #
#                                                       THE MAIN FUNCTION                                                                       #
# --------------------------------------------------------------------------------------------------------------------------------------------- #
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=7004, debug=True)
