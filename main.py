import  logging
import  json
from    flask      import Flask
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


logging.basicConfig(level=logging.DEBUG)
app             = Flask(__name__)

default_error   = json.dumps({"error_code": 500, "error_message": "Internal server error", "display_message": ""})

print("working")
@app.route("/v1")
def working():
    return "user-booking service running"

#@app.route("/v1/book")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7003, debug=True, ssl_context='adhoc')
