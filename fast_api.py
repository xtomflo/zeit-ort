from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request, Form
import uvicorn

from flask_selfdoc import Autodoc
from ipaddress import ip_address
import json
import sqlite3
import git
import python.config as config
import requests

app = FastAPI()

def db_connection():
    conn = None
    try:
        conn = sqlite3.connect("zeit-ort.db")
    except sqlite3.error as e:
        print(e)

    conn.set_trace_callback(print)
    return conn, conn.cursor()

def get_sql_result(cursor, count = 'one'):

    if(count == 'one'):
        result = list(cursor.fetchone())
        keys = [description[0] for description in cursor.description]
    elif(count == 'all'):
        # ------- to be fixed
        result = cursor.fetchall()
        keys = [description[0] for description in cursor.description]

    return result, keys

# Fire Request for Weather
def get_weather(params):

    payload = {'appid': config.OPENWEATHER_KEY, 'lat': params['latitude'], 'lon': params['longitude'], 'units':'metric', 'exclude' :'current,minutely,hourly,alerts'}
    r = requests.get("https://api.openweathermap.org/data/2.5/onecall",params=payload)
    
    return r.json()

# Extract key weather info
def clean_weather(weather_json):
    print('hi')


@app.get("/api/ip_weather")
def get_ip_weather():

    # Get IP From the request
    ip_input = request.args.get('ip',None)

    try: 
        # Convert the IP address to Int
        ip_input = int(ip_address(ip_input))
    except Exception as e:
        return ("Input error: {0}".format(e))

    # Connect to the database
    conn, cursor = db_connection()

    # Get a single location matching the IP address
    cursor = conn.execute("SELECT country_iso, region_iso, region_name, city_name, latitude, longitude \
     FROM ip_location WHERE ? BETWEEN ip_range_start AND ip_range_end LIMIT 1;", (ip_input,))

    # Read the result
    ip_results, ip_keys = get_sql_result(cursor)
    # Convert results to a dictionary
    location =dict(zip(ip_keys,ip_results))

    weather = get_weather(location)

    return weather


@app.get("/api/ip_location")
def get_ip_location():
    """ Get Location for the given IP Address """

    # Get IP From the request
    ip_input = request.args.get('ip',None)
    try: 
        # Convert the IP address to Int
        ip_input = int(ip_address(ip_input))
    except Exception as e:
        return ("Input error: {0}".format(e))

    # Connect to the database
    conn, cursor = db_connection()

    # Get a single location matching the IP address
    cursor = conn.execute("SELECT country_iso, region_iso, region_name, city_name \
     FROM ip_location WHERE ? BETWEEN ip_range_start AND ip_range_end LIMIT 1;", (ip_input,))
    
    # Read the result
    ip_results, ip_keys = get_sql_result(cursor)
    # Convert results to a dictionary
    location =dict(zip(ip_keys,ip_results))

    if location is not None:
        return jsonify(location)

# Get holidays for next 7 days
@app.get("/api/get_holidays")
def get_holidays():
    """ 
    Get global Holidays for the given data and period 
    """
    date   = request.args.get('date', None)     # ---- validate date format
    period   = request.args.get('period', 7)
    period = "+{} days".format(period)

    # Connect to the database
    conn, cursor  = db_connection()

    cursor = conn.execute("SELECT * FROM flat_holidays WHERE date_iso BETWEEN date(?) AND date(?,?)",(date,date,period))

    result = cursor.fetchall()

    if result is not None:
        return jsonify(result)

@app.get("/api/is_holiday", response_class=JSONResponse)
async def is_holiday(ip: str, date: str ='now', period: int = 7):

    """
    Check whether it is a holiday is given location
    """
    try: 
        # Convert the IP address to Int
        ip_input = int(ip_address(ip))
    except Exception as e:
        return ("Input error: {0}".format(e))  

    # Get the period from the request & convert to string for SQL
    period   = "+{} days".format(period)

    # Connect to the database
    conn, cursor = db_connection()
    
    # Get a single location matching the IP address
    cursor = conn.execute("SELECT country_iso, region_iso, region_name, city_name \
     FROM ip_location WHERE ? BETWEEN ip_range_start AND ip_range_end LIMIT 1;", (ip_input,))
    
    # Read the result
    ip_results, ip_keys = get_sql_result(cursor)
    # Convert results to a dictionary
    location =dict(zip(ip_keys,ip_results))

    # Query holidays in the upcoming X days for Y country or Z region
    cursor = conn.execute("SELECT * FROM flat_holidays WHERE date_iso BETWEEN date(?) AND date(?,?) \
        AND country_iso=? AND (all_states=1 OR region_iso=?)",(date,date,period,location['country_iso'],location['region_iso']))

    result = cursor.fetchone()


    if result is not None:
        return result
    else:
        return "None"

@app.get("/api/get_country_holidays")
def get_country_holidays():
    """
    Get holidays per country or country region
    """ 
    date = request.args.get('date', 'now')       # ---- validate date format
    country  = request.args.get('country',None)
    region   = request.args.get('region',None)
    # Get the period from the request & convert to string for SQL
    period   = request.args.get('period', 7)

    
    period   = "+{} days".format(period)

    # Connect to the database
    conn, cursor = db_connection()

    cursor = conn.execute("SELECT * FROM flat_holidays WHERE date_iso BETWEEN date(?) AND date(?,?) \
     AND (country_iso=? OR region_iso=?)",(date,date,period,country,region))

    result = cursor.fetchall()

    #---------------------------------------------------------- ADD CHECK FOR NO HOLIDAYS 
    if result is not None:
    	return jsonify(result)

@app.get("/api/get_ip_holidays")
def get_ip_holidays():
    """ 
    Get holidays per given IP address
    """
    date = request.args.get('date', 'now')
    # Get IP from the request
    ip_input = request.args.get('ip',None)
    try: 
        # Convert the IP address to Int
        ip_input = int(ip_address(ip_input))
    except Exception as e:
        return ("Input error: {0}".format(e))    

    # Get the period from the request & convert to string for SQL
    period   = request.args.get('period', 7)
    period   = "+{} days".format(period)

    # Connect to the database
    conn, cursor = db_connection()
    
   	# Get a single location matching the IP address
    cursor = conn.execute("SELECT country_iso, region_iso, region_name, city_name \
     FROM ip_location WHERE ? BETWEEN ip_range_start AND ip_range_end LIMIT 1;", (ip_input,))
    
    # Read the result
    ip_results, ip_keys = get_sql_result(cursor)
    # Convert results to a dictionary
    location =dict(zip(ip_keys,ip_results))

    # Query holidays in the upcoming X days for Y country or Z region
    cursor = conn.execute("SELECT * FROM flat_holidays WHERE date_iso BETWEEN date(?) AND date(?,?) \
        AND country_iso=? AND (all_states=1 OR region_iso=?)",(date,date,period,location['country_iso'],location['region_iso']))

    result = cursor.fetchall()

    if result is not None:
        return jsonify(result)

@app.get("/api/get_ip_density")
def get_ip_density():
    """
    Get location density score for given IP address
    """
    # Get IP From the request
    ip_input = request.args.get('ip',None)
    try: 
        # Convert the IP address to Int
        ip_input = int(ip_address(ip_input))
    except Exception as e:
        return ("Input error: {0}".format(e))  

    # Connect to the database
    conn, cursor = db_connection()

    # Get a single location matching the IP address
    cursor = conn.execute("SELECT country_iso, region_iso, region_name, city_name, latitude, longitude \
     FROM ip_location WHERE ? BETWEEN ip_range_start AND ip_range_end LIMIT 1;", (ip_input,))
    
    # Read the  IP query result
    ip_results, ip_keys = get_sql_result(cursor)
    # Convert results to a dictionary
    location =dict(zip(ip_keys,ip_results))
    
    cursor = conn.execute("SELECT density FROM opencell_density WHERE latitude = ROUND(?,1) AND longitude = ROUND(?,1)",(location['latitude'],location['longitude']))

    # Read the Density query result
    density_results, density_keys = get_sql_result(cursor)
    
    results, keys = ip_results + density_results, ip_keys + density_keys
    final_result = dict(zip(keys,results))

    if results is not None:
        return jsonify(final_result)

@app.get("/api/get_all")
def get_all():
    """
    Get Location, holidays and density score for a given IP address
    """
    # Get Date
    date = request.args.get('date', 'now')
    # Get IP From the request
    ip_input = request.args.get('ip',None)
    try: 
        # Convert the IP address to Int
        ip_input = int(ip_address(ip_input))
    except Exception as e:
        return ("Input error: {0}".format(e))  
    # Get the period from the request & convert to string for SQL
    period   = request.args.get('period', 7)
    period   = "+{} days".format(period)

    # Connect to the database
    conn, cursor = db_connection()

    # Get a single location matching the IP address
    cursor = conn.execute("SELECT country_iso, region_iso, region_name, city_name, latitude, longitude \
     FROM ip_location WHERE ? BETWEEN ip_range_start AND ip_range_end LIMIT 1;", (ip_input,))

    # Read the result
    ip_results, ip_keys = get_sql_result(cursor)

    # Convert results to a dictionary
    location = dict(zip(ip_keys,ip_results))

    # Query for density score
    cursor = conn.execute("SELECT density as density_score FROM opencell_density WHERE latitude = ROUND(?,1) \
     AND longitude = ROUND(?,1)",(location['latitude'],location['longitude']))

    density_results, density_keys = get_sql_result(cursor)

    # Query holidays in the upcoming X days for Y country or Z region
    cursor = conn.execute("SELECT * FROM flat_holidays WHERE date_iso BETWEEN date(?) AND date(?,?) AND \
     country_iso=? AND (all_states=1 OR region_iso=?)",(date,date, period,location['country_iso'],location['region_iso']))

    holiday_results, holiday_keys = get_sql_result(cursor,'all')

    result,keys = ip_results + density_results + holiday_results,ip_keys + density_keys + holiday_keys

    final_result = dict(zip(keys,result))

    if result is not None:
        return jsonify(final_result)

#@app.get('/documentation')
#def documentation():
#    return auto.html()

@app.get("/test")
def get_test():
	return "Auto Deployment is working!? Yes it is! (with Debug mode)"

@app.post('/update_server')
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


@app.get("/")
def hello_world():
    return "<p>Hello, Outer  World!</p>"

if __name__ == '__main__':
    uvicorn.run('api:app', host='0.0.0.0', port=8000)
# Get Holidays for IP Address