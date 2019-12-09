class Fare:

    @staticmethod
    def get_fare(from_latitude, from_longitude, to_latitude, to_longitude):
        try:
            # Calculate distance between the given distances
            payment = 10
            resu
            return payment
        except Exception as e:
            if conn is not None:
                conn.close()
            logging.error("Error in creating booking: " + str(e))
            error = Response.make_error(error_message = "System failure", error_code = 500, display_message = "Oops something went wrong !")
            return -1
