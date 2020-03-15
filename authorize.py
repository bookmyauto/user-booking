"""
                Description : contains code for authorization
                Author      : Rahul Tudu
"""
import  jwt
import  requests
from    datetime import  datetime
import  logging


class Authorize:

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    #                                                   VERTIFYING JWT AND EXPIRY TIME                                                                                          #
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    @staticmethod
    def verify_jwt(token):
        try:
            payload                 = jwt.decode(token, verify = False)
            timestamp               = datetime.timestamp(datetime.now())
            payload_number          = payload["number"]
            expiry_timestamp        = payload["exp"]
            logging.debug("  " + str(payload_number) + ":  Payload decrypted")
            if timestamp <= expiry_timestamp:
                _                   = jwt.decode(token, 'mandolin', algorithm = 'HS256')
                logging.debug("  " + str(payload_number) + ":  Signature decoded")
                return 1, ""
            else:
                response        = requests.get("http://127.0.0.1:8080/v1/getJWT?number=" + str(payload_number))
                logging.debug("  " + str(payload_number) + ":  New token fetched")
                response        = response.json()
                if response["token"] == "":
                    raise ValueError
                else:
                    return 1, response["token"]

        except Exception as e:
            logging.critical("  " + str(payload_number) + ":  Error in verify_jwt authorization: " + str(e))
            return 0, ""

