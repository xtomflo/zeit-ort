from flask import Flask, request, jsonify
from ipaddress import ip_address
import json
import sqlite3

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

@app.route("/api/json/ip_location", methods = ["GET"])
def get_json_ip_location(ip_input):
	json_data = flask.request.json


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

if __name__ == "__main__":
    app.run(port=5000, debug=True)
# Get Holidays for IP Address