import  logging
import  json
from    flask      import Flask


logging.basicConfig(level=logging.DEBUG)
app             = Flask(__name__)

default_error   = json.dumps({"error_code": 500, "error_message": "Internal server error", "disaply_message": ""})


@app.route("/v1")
def working():
    return "user-booking service running"

@app.route("/v1/book")

if __name__ == '__main__':
    app.run(port=7002, debug=True)
