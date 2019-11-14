import logging


class Response:
    # create an error data
    @staticmethod
    def make_error(error_code, error_message, display_message):
        error               = {"error_code": str(error_code), "error_message": str(error_message),
                               "display_message": str(display_message)}
        return error

    # create a result data
    @staticmethod
    def make_result(result_code, result_message, display_message, **kwargs):
        result              = {"result_code": str(result_code), "result_message": str(result_message),
                               "display_message": str(display_message)}
        logging.info("result maker has received")
        for key, value in kwargs.items():
            result[key]     = value
        return result
