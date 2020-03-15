"""
                Description : contains code for getting fare
                Author      : Rahul Tudu
"""
import logging
from response import Response


class Fare:

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    #                                                   GET FARE                                                                                                                #
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    @staticmethod
    def get_fare(from_latitude, from_longitude, to_latitude, to_longitude):
        try:
            # Calculate distance between the given distances
            payment = 10
            return payment
        except Exception as e:
            logging.error("  Error in creating booking: " + str(e))
            error = Response.make_error(error_message = "System failure", error_code = 500, display_message = "Oops something went wrong !")
            return -1
