"""
                Description : contains code for making response
                Author      : Rahul Tudu
"""
import logging
import json


class Response:

    default_error   = json.dumps({"error_code": 500, "error_message": "Internal server error", "display_message": ""})

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    #                                                   Makes response                                                                                                          #
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    @staticmethod
    def make_response(http_code, message, display_message, **kwargs):
        result              = {"httpCode": str(http_code), "message": str(message),
                               "displayMessage": str(display_message), "data": {}}
        logging.debug("  Result maker has received")
        for key, value in kwargs.items():
            result["data"][key]     = value
        return result
