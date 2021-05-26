from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request, Form
from flask_selfdoc import Autodoc
from ipaddress import ip_address
import python.config as config
import python.utils as utils
import uvicorn
import json
import sqlite3
import git
import requests
from datetime import date

app = FastAPI()

@app.get("/api/ip_weather")
def get_ip_weather(ip: str):

    ip = utils.validate_ip(ip)

    # Connect to the database
    conn, cursor = utils.db_connection()

    # Get a single location matching the IP address
    cursor = conn.execute("SELECT country_iso, region_iso, region_name, city_name, latitude, longitude \
     FROM ip_location WHERE ? BETWEEN ip_range_start AND ip_range_end LIMIT 1;", (ip,))

    # Read the result
    ip_results, ip_keys = utils.get_sql_result(cursor)
    # Convert results to a dictionary
    location = dict(zip(ip_keys,ip_results))

    weather = utils.get_weather(location)
    #print(weather)
    weather_json = json.loads(weather)

    for day in weather_json['daily']:
        #print(day)
        #print("Easy", day['weather'], day['temp'])
        print("Hard", day['weather'][0]['description'], day['temp']['day'])

    return weather


@app.get("/api/ip_location")
def get_ip_location(ip: str):
    """ Get Location for the given IP Address """

    ip = utils.validate_ip(ip)

    # Connect to the database
    conn, cursor = utils.db_connection()

    # Get a single location matching the IP address
    cursor = conn.execute("SELECT country_iso, region_iso, region_name, city_name \
     FROM ip_location WHERE ? BETWEEN ip_range_start AND ip_range_end LIMIT 1;", (ip,))
    
    # Read the result
    ip_results, ip_keys = utils.get_sql_result(cursor)
    # Convert results to a dictionary
    location =dict(zip(ip_keys,ip_results))

    if location is not None:
        return location

# Get holidays for next 7 days
@app.get("/api/get_holidays")
def get_holidays(date: date = 'now', period: int = 7):
    """ 
    Get global Holidays for the given data and period 
    """
   
    period = utils.wrap_period(period)

    # Connect to the database
    conn, cursor  = utils.db_connection()

    cursor = conn.execute("SELECT * FROM flat_holidays WHERE date_iso BETWEEN date(?) AND date(?,?)",(date,date,period))

    result = cursor.fetchall()

    if result is not None:
        return result

@app.get("/api/is_holiday", response_class=JSONResponse)
def is_holiday(ip: str, date: date ='now', period: int = 0):

    """
    Check whether it is a holiday is given location
    """
   
    ip = utils.validate_ip(ip)  

    # Convert period to "+ X days" for SQL query
    period   = utils.wrap_period(period)

    # Connect to the database
    conn, cursor = utils.db_connection()
    print("IP ----------------------",ip)
    # Get a single location matching the IP address
    cursor = conn.execute("SELECT country_iso, region_iso, region_name, city_name \
     FROM ip_location WHERE ? BETWEEN ip_range_start AND ip_range_end LIMIT 1;", (ip,))
    
    # Read the result
    ip_results, ip_keys = utils.get_sql_result(cursor)

    # Convert results to a dictionary
    location =dict(zip(ip_keys,ip_results))
    print(location)

    # Query holidays in the upcoming X days for Y country or Z region
    cursor = conn.execute("SELECT * FROM flat_holidays WHERE date_iso BETWEEN date(?) AND date(?,?) \
        AND country_iso=? AND (all_states=1 OR region_iso=?)",(date,date,period,location['country_iso'],location['region_iso']))

    result = cursor.fetchone()


    if result is not None:
        return result
    else:
        return "None"

@app.get("/api/get_country_holidays")
def get_country_holidays(country: str, region: str, date: date ='now', period: int = 7):
    """
    Get holidays per country or country region
    """ 
    
    # Convert period to "+ X days" for SQL query
    period   = utils.wrap_period(period)

    # Connect to the database
    conn, cursor = utils.db_connection()

    cursor = conn.execute("SELECT * FROM flat_holidays WHERE date_iso BETWEEN date(?) AND date(?,?) \
     AND (country_iso=? OR region_iso=?)",(date,date,period,country,region))

    result = cursor.fetchall()

    #---------------------------------------------------------- ADD CHECK FOR NO HOLIDAYS 
    if result is not None:
    	return result

@app.get("/api/get_ip_holidays")
def get_ip_holidays(ip: str, date: date ='now', period: int = 7):
    """ 
    Get holidays per given IP address
    """
    # Validate IP address
    ip = utils.validate_ip(ip)    
    # Convert period to "+ X days" for SQL query
    period   = utils.wrap_period(period)
    # Connect to the database
    conn, cursor = utils.db_connection()
    
   	# Get a single location matching the IP address
    cursor = conn.execute("SELECT country_iso, region_iso, region_name, city_name \
     FROM ip_location WHERE ? BETWEEN ip_range_start AND ip_range_end LIMIT 1;", (ip,))
    
    # Read the result
    ip_results, ip_keys = utils.get_sql_result(cursor)
    # Convert results to a dictionary
    location =dict(zip(ip_keys,ip_results))

    # Query holidays in the upcoming X days for Y country or Z region
    cursor = conn.execute("SELECT * FROM flat_holidays WHERE date_iso BETWEEN date(?) AND date(?,?) \
        AND country_iso=? AND (all_states=1 OR region_iso=?)",(date,date,period,location['country_iso'],location['region_iso']))

    result = cursor.fetchall()

    if result is not None:
        return result

@app.get("/api/get_ip_density")
def get_ip_density(ip: str):
    """
    Get location density score for given IP address
    """
    # Validate IP address
    ip = utils.validate_ip(ip)  

    # Connect to the database
    conn, cursor = utils.db_connection()

    # Get a single location matching the IP address
    cursor = conn.execute("SELECT country_iso, region_iso, region_name, city_name, latitude, longitude \
     FROM ip_location WHERE ? BETWEEN ip_range_start AND ip_range_end LIMIT 1;", (ip,))
    
    # Read the  IP query result
    ip_results, ip_keys = utils.get_sql_result(cursor)
    # Convert results to a dictionary
    location =dict(zip(ip_keys,ip_results))
    
    cursor = conn.execute("SELECT density FROM opencell_density WHERE latitude = ROUND(?,1) AND longitude = ROUND(?,1)",(location['latitude'],location['longitude']))

    # Read the Density query result
    density_results, density_keys = utils.get_sql_result(cursor)
    
    results, keys = ip_results + density_results, ip_keys + density_keys
    final_result = dict(zip(keys,results))

    if results is not None:
        return final_result

@app.get("/api/get_all")
def get_all(ip: str, date: date ='now', period: int = 7):
    """
    Get Location, holidays and density score for a given IP address
    """

    ip = utils.validate_ip(ip)  

    period   = utils.wrap_period(period)

    # Connect to the database
    conn, cursor = utils.db_connection()

    # Get a single location matching the IP address
    cursor = conn.execute("SELECT country_iso, region_iso, region_name, city_name, latitude, longitude \
     FROM ip_location WHERE ? BETWEEN ip_range_start AND ip_range_end LIMIT 1;", (ip,))

    # Read the result
    ip_results, ip_keys = utils.get_sql_result(cursor)

    # Convert results to a dictionary
    location = dict(zip(ip_keys,ip_results))

    # Query for density score
    cursor = conn.execute("SELECT density as density_score FROM opencell_density WHERE latitude = ROUND(?,1) \
     AND longitude = ROUND(?,1)",(location['latitude'],location['longitude']))

    density_results, density_keys = utils.get_sql_result(cursor)

    # Query holidays in the upcoming X days for Y country or Z region
    cursor = conn.execute("SELECT * FROM flat_holidays WHERE date_iso BETWEEN date(?) AND date(?,?) AND \
     country_iso=? AND (all_states=1 OR region_iso=?)",(date,date, period,location['country_iso'],location['region_iso']))

    holiday_results, holiday_keys = utils.get_sql_result(cursor,'all')

    result,keys = ip_results + density_results + holiday_results,ip_keys + density_keys + holiday_keys

    final_result = dict(zip(keys,result))

    if result is not None:
        return final_result

#@app.get('/documentation')
#def documentation():
#    return auto.html()

@app.get("/test")
def get_test():
	return "Auto Deployment is working!? Yes it is! (with Debug mode)"


@app.get("/")
def hello_world():
    return "<p>Hello, Outer  World!</p>"

if __name__ == '__main__':
    uvicorn.run('fast_api:app', reload=True, host='0.0.0.0', port=8000)
# Get Holidays for IP Address
