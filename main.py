import  logging
import  requests
import  json
from    flask   import Flask
from    flask   import request
from    book    import Book
from    urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


logging.basicConfig(level=logging.DEBUG)
app             = Flask(__name__)

default_error   = json.dumps({"error_code": 500, "error_message": "Internal server error", "display_message": ""})

print("user-booking started")
@app.route("/v1")
def working():
    return "user-booking service running"

@app.route("/v1/book", methods=["POST"])
def book():
    try:
        if request.method == "POST":
            user_number     = request.form["number"]
            if "fromLatitude" in request.form:
                from_latitude   = request.form["fromLatitude"]
                from_longitude  = request.form["fromLongitude"]
                to_latitude     = request.form["toLatitude"]
                to_longitude    = request.form["toLongitude"]
                response        = json.dumps(Book.create_booking(user_number, from_longitude, from_latitude, to_longitude, to_latitude))
                return response
            else:
                response    = json.dumps(Book.cancel_booking(user_number))
                return response
    except RuntimeError as e:
        logging.critical("failure in v1/book with error: " + str(e))
        return default_error

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7003, debug=True, ssl_context='adhoc')
