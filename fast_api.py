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
    cursor = utils.get_ip_location(conn, (ip,))

    # Read the result
    ip_results, ip_keys = utils.get_sql_result(cursor)
    # Convert results to a dictionary
    location = utils.convert(ip_keys,ip_results)

    weather = utils.get_weather(location)
    weather_json = json.loads(weather)

    weather = utils.clean_weather(weather_json)
    
    return weather


@app.get("/api/ip_location")
def get_ip_location(ip: str):
    """ Get Location for the given IP Address """

    ip = utils.validate_ip(ip)

    # Connect to the database
    conn, cursor = utils.db_connection()

    # Get a single location matching the IP address
    cursor = utils.get_ip_location(conn, (ip,))
    
    # Read the result
    ip_results, ip_keys = utils.get_sql_result(cursor)

    # Convert results to a dictionary
    location = utils.convert(ip_keys,ip_results)

    if location is not None:
        return location

   
# Get holidays for next 7 days
@app.get("/api/get_global_holidays")
def get_global_holidays(date: date = 'now', period: int = 7):
    """ 
    Get global Holidays for a period starting on the given date. By default next week.
    """
   
    period = utils.wrap_period(period)

    # Connect to the database
    conn, cursor  = utils.db_connection()

    cursor = utils.get_global_holidays(conn,(date,date,period))

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
    cursor = utils.get_ip_location(conn,(ip,))
    
    # Read the result
    ip_results, ip_keys = utils.get_sql_result(cursor)

    # Convert results to a dictionary
    location = utils.convert(ip_keys,ip_results)

    # Query holidays in the upcoming X days for Y country or Z region
    cursor = utils.get_local_holidays(conn ,(date,date,period,location['country_iso'],location['region_iso']))

    result = cursor.fetchone()


    if result is not None:
        return result
    else:
        return "None"

@app.get("/api/get_local_holidays")
def get_local_holidays(country: str, region: str, date: date ='now', period: int = 7):
    """
    Get holidays per country or country region
    """ 
    
    # Convert period to "+ X days" for SQL query
    period   = utils.wrap_period(period)

    # Connect to the database
    conn, cursor = utils.db_connection()

    cursor = utils.get_local_holidays(conn,(date,date,period,country,region))

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
    cursor = utils.get_ip_location(conn,(ip,))
    
    # Read the result
    ip_results, ip_keys = utils.get_sql_result(cursor)
    # Convert results to a dictionary
    location =utils.convert(ip_keys,ip_results)

    # Query holidays in the upcoming X days for Y country or Z region
    cursor = utils.get_local_holidays(conn ,(date,date,period,location['country_iso'],location['region_iso']))

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
    cursor = utils.get_ip_location(conn, (ip,))
    
    # Read the  IP query result
    ip_results, ip_keys = utils.get_sql_result(cursor)
    # Convert results to a dictionary
    location =utils.convert(ip_keys,ip_results)
    
    cursor = utils.get_density(conn,(location['latitude'],location['longitude']))

    # Read the Density query result
    density_results, density_keys = utils.get_sql_result(cursor)
    
    results, keys = ip_results + density_results, ip_keys + density_keys
    final_result = dict(zip(keys,results))

    if results is not None:
        return final_result

@app.get("/api/get_all")
def get_all(ip: str, date: date ='now', period: int = 0):
    """
    Get Location, holidays and density score for a given IP address
    """

    ip = utils.validate_ip(ip)  

    period   = utils.wrap_period(period)

    # Connect to the database
    conn, cursor = utils.db_connection()

    # Get a single location matching the IP address
    cursor = utils.get_ip_location(conn, (ip,))

    # Read the result
    ip_results, ip_keys = utils.get_sql_result(cursor)

    # Convert results to a dictionary
    location = utils.convert(ip_keys,ip_results)

    weather = utils.get_weather(location)
    weather_json = json.loads(weather)
    weather = utils.clean_weather(weather_json)

    weather_keys, weather_results = list(weather.keys()), list(weather.values())

    # Query for density score
    cursor = utils.get_density(conn,(location['latitude'],location['longitude']))

    density_results, density_keys = utils.get_sql_result(cursor)

    # Query holidays in the upcoming X days for Y country or Z region
    cursor = utils.get_local_holidays(conn, (date,date, period,location['country_iso'],location['region_iso']))

    #holiday_results, holiday_keys = utils.get_sql_result(cursor,'all')
    holiday_results, holiday_keys = utils.get_sql_result(cursor)

    holiday_keys = ['is_holiday']
    holiday_results = ['true'] if holiday_results is not None else ['false']

    
    result,keys = ip_results + density_results + holiday_results + weather_results,ip_keys + density_keys + holiday_keys + weather_keys

    final_result = utils.convert(keys,result)

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
