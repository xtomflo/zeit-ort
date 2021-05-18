from flask import Flask, request, jsonify, abort
from ipaddress import ip_address
import json
import sqlite3
import git


app = Flask(__name__)

def db_connection():
    conn = None
    try:
        conn = sqlite3.connect("zeit-ort.db")
    except sqlite3.error as e:
        print(e)
    return conn


# Get Location from IP Address
@app.route("/api/ip_location/<string:ip_input>", methods = ["GET"])
def get_ip_location(ip_input):
	# Connect to the database
    conn = db_connection()
    cursor = conn.cursor()

    # Get the IP address from input
    ip_addr = ip_address(ip_input)
    # Convert IP address to INT
    ip_addr = int(ip_addr)
   	# Get a single location matching the IP address
    cursor = conn.execute("SELECT country_iso_code, subdivision_1_iso_code, subdivision_1_name, city_name \
     FROM ip_locations WHERE ? BETWEEN ip_range_start AND ip_range_end LIMIT 1;", (ip_addr,))
    # Read the result
    result = cursor.fetchone()
    
    location =dict(country_iso=result[0], region_iso=result[1], region_name=result[2], city_name=result[3])

    if location is not None:
   		return jsonify(location)

@app.route("/api/get_holidays/<string:date>")
def get_holidays(date):
	something = 0

@app.route("/test")
def get_test():
	return "Auto Deployment is working!?"

@app.route("/api/json/ip_location", methods = ["GET"])
def get_json_ip_location(ip_input):
	json_data = flask.request.json

@app.route('/update_server', methods=['POST'])
def webhook():
	# Read request
    x_hub_signature = request.headers.get('X-Hub-Signature')
    # Validate key from request
#    if not is_valid_signature(x_hub_signature, request.data, w_secret):
#        print('Deploy signature failed: {sig}'.format(sig=x_hub_signature))
#        abort(418)
    # Check the request method. Other Checks can be added
    if request.method == 'POST':
    	# Local location of the repo
        repo = git.Repo('../zeit-ort')
        origin = repo.remotes.origin
        # Pull the repo to be updated
        origin.pull()
        return 'Updated zeit-ort App successfully', 200
    else:
        return 'Wrong event type', 400


@app.route("/")
def hello_world():
    return "<p>Hello, Outer  World!</p>"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
# Get Holidays for IP Address
