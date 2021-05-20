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
    cursor = conn.execute("SELECT country_iso, region_iso, region_name, city_name \
     FROM ip_location WHERE ? BETWEEN ip_range_start AND ip_range_end LIMIT 1;", (ip_addr,))
    # Read the result
    result = cursor.fetchone()
    
    location =dict(country_iso=result[0], region_iso=result[1], region_name=result[2], city_name=result[3])

    if location is not None:
   		return jsonify(location)

# Get holidays for next 7 days
@app.route("/api/get_holidays/")
def get_holidays():
	# Connect to the database
    conn = db_connection()
    cursor = conn.cursor()

    cursor = conn.execute("SELECT * FROM flat_holidays WHERE date_iso BETWEEN date('now') AND date('now','+? days')"),(period,)

    result = cursor.fetchall()

    if result is not None:
    	return jsonify(result)

@app.route("/api/get_country_holidays/<string:country>", methods = ["GET"])
def get_country_holidays(country):
	# Connect to the database
    conn = db_connection()
    cursor = conn.cursor()

    cursor = conn.execute("SELECT * FROM flat_holidays WHERE date_iso BETWEEN date('now') AND date('now','+7 days') AND country_iso=?",(country,))

    result = cursor.fetchall()

    if result is not None:
    	return jsonify(result)

@app.route("/api/get_ip_holiday/")
def get_ip_holidays():
    # Get IP From the request
    #---------------------------------------------------------- ADD CHECKING VALIDITY OF THE IP ADDRESS
    ip_input = request.args.get('ip',None)
    # Get the period from the request & convert to string for SQL
    period   = request.args.get('period', 7)
    #---------------------------------------------------------- ADD LIMIT OF DAYS TO BE QUERIED
    period   = "+{} days".format(period)

    # Connect to the database
    conn = db_connection()
    cursor = conn.cursor()

    # Get the IP address from input
    ip_addr = ip_address(ip_input)
    # Convert IP address to INT
    ip_addr = int(ip_addr)
   	# Get a single location matching the IP address
    cursor = conn.execute("SELECT country_iso, region_iso, region_name, city_name \
     FROM ip_location WHERE ? BETWEEN ip_range_start AND ip_range_end LIMIT 1;", (ip_addr,))
    # Read the result
    result = cursor.fetchone()
    # Convert results to a dictionary
    location =dict(country_iso=result[0], region_iso=result[1], region_name=result[2], city_name=result[3])
    print(location)

    # Query holidays in the upcoming X days for Y country or Z region
    cursor = conn.execute("SELECT * FROM flat_holidays WHERE date_iso BETWEEN date('now') AND date('now',?) AND country_iso=? AND (all_states=1 OR region_iso=?)",(period,location['country_iso'],location['region_iso']))

    result = cursor.fetchall()

    if result is not None:
    	return jsonify(result)

@app.route("/api/get_ip_density/")
def get_ip_density():
    # Get IP From the request
    #---------------------------------------------------------- ADD CHECKING VALIDITY OF THE IP ADDRESS
    ip_input = request.args.get('ip',None)
    # Connect to the database
    conn = db_connection()
    cursor = conn.cursor()

    # Get the IP address from input
    ip_addr = ip_address(ip_input)
    # Convert IP address to INT
    ip_addr = int(ip_addr)
    # Get a single location matching the IP address
    cursor = conn.execute("SELECT country_iso, region_iso, region_name, city_name, latitude, longitude \
     FROM ip_location WHERE ? BETWEEN ip_range_start AND ip_range_end LIMIT 1;", (ip_addr,))
    # Read the result
    ip_result = list(cursor.fetchone())
    ip_keys = [description[0] for description in cursor.description]

    # Convert results to a dictionary
    location =dict(country_iso=ip_result[0], region_iso=ip_result[1], region_name=ip_result[2], city_name=ip_result[3], latitude=ip_result[4], longitude=ip_result[5])

    cursor = conn.execute("SELECT density FROM opencell_density WHERE latitude = ROUND(?,1) AND longitude = ROUND(?,1)",(location['latitude'],location['longitude']))

    density_result = list(cursor.fetchone())
    density_keys = [description[0] for description in cursor.description]
    
    result,keys = ip_result + density_result,ip_keys + density_keys

    final_result = zip(keys,result)
    dict_result = dict(final_result)

    print(dict_result)
    for name, val in final_result:
        print(name, val)

    if result is not None:
        return jsonify(dict_result)

@app.route("/api/get_all/")
def get_all():
    # Get IP From the request
    #---------------------------------------------------------- ADD CHECKING VALIDITY OF THE IP ADDRESS
    ip_input = request.args.get('ip',None)
    # Get the period from the request & convert to string for SQL
    period   = request.args.get('period', 7)
    #---------------------------------------------------------- ADD LIMIT OF DAYS TO BE QUERIED
    period   = "+{} days".format(period)

    # Connect to the database
    conn = db_connection()
    cursor = conn.cursor()
    
    # Get the IP address from input
    ip_addr = ip_address(ip_input)
    # Convert IP address to INT
    ip_addr = int(ip_addr)
    # Get a single location matching the IP address
    cursor = conn.execute("SELECT country_iso, region_iso, region_name, city_name, latitude, longitude \
     FROM ip_location WHERE ? BETWEEN ip_range_start AND ip_range_end LIMIT 1;", (ip_addr,))
    # Read the result
    ip_result = list(cursor.fetchone())
    ip_keys = [description[0] for description in cursor.description]

    # Convert results to a dictionary
    location =dict(country_iso=ip_result[0], region_iso=ip_result[1], region_name=ip_result[2], city_name=ip_result[3], latitude=ip_result[4], longitude=ip_result[5])

    cursor = conn.execute("SELECT density FROM opencell_density WHERE latitude = ROUND(?,1) AND longitude = ROUND(?,1)",(location['latitude'],location['longitude']))

    density_result = list(cursor.fetchone())
    density_keys = [description[0] for description in cursor.description]

    # Query holidays in the upcoming X days for Y country or Z region
    cursor = conn.execute("SELECT * FROM flat_holidays WHERE date_iso BETWEEN date('now') AND date('now',?) AND country_iso=? AND (all_states=1 OR region_iso=?)",(period,location['country_iso'],location['region_iso']))

    holiday_result = list(cursor.fetchone())
    holiday_keys = [description[0] for description in cursor.description]

    result,keys = ip_result + density_result + holiday_result,ip_keys + density_keys + holiday_keys

    final_result = zip(keys,result)
    dict_result = dict(final_result)

    print(dict_result)
    for name, val in final_result:
        print(name, val)

    if result is not None:
        return jsonify(dict_result)


@app.route("/test")
def get_test():
	return "Auto Deployment is working!? Yes it is! (with Debug mode)"

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
