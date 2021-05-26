from ipaddress import ip_address
import python.config as config
import sqlite3
import requests

def db_connection():
    conn = None
    try:
        conn = sqlite3.connect("zeit-ort.db")
    except sqlite3.error as e:
        print(e)

    conn.set_trace_callback(print)
    return conn, conn.cursor()

def validate_ip(ip):
    try: 
        # Convert the IP address to Int
        ip_input = int(ip_address(ip))
    except Exception as e:
        return ("Input error: {0}".format(e))

    return ip_input

def wrap_period(period):
    return "+{} days".format(period)

def convert(keys,results):
    return dict(zip(keys,results))

def get_sql_result(cursor, count = 'one'):

    output = cursor.fetchone()
    if(count == 'one'):
        result = list(output) if output is not None else None
        keys = [description[0] for description in cursor.description]
    elif(count == 'all'):
        # ------- to be fixed
        result = cursor.fetchall()
        keys = [description[0] for description in cursor.description]

    return result, keys

# Fire Request for Weather
def get_weather(params):

    payload = {'appid': config.OPENWEATHER_KEY, 'lat': params['latitude'], 'lon': params['longitude'],\
     'units':'metric', 'exclude' :'current,minutely,hourly,alerts'}
    r = requests.get("https://api.openweathermap.org/data/2.5/onecall",params=payload)
    
    return r.text

def get_ip_location(conn, params):
    return conn.execute("SELECT country_iso, region_iso, region_name, city_name, latitude, longitude \
     FROM ip_location WHERE ? BETWEEN ip_range_start AND ip_range_end LIMIT 1;",params)

def get_ip_location_custom(conn,params):
    return conn.execute("SELECT ? \
     FROM ip_location WHERE ? BETWEEN ip_range_start AND ip_range_end LIMIT 1;",params)

def get_global_holidays(conn, params):
    return conn.execute("SELECT * FROM flat_holidays WHERE date_iso BETWEEN date(?) AND date(?,?)",params)

def get_local_holidays(conn,params):
    return conn.execute("SELECT * FROM flat_holidays WHERE date_iso BETWEEN date(?) AND date(?,?) \
        AND country_iso=? AND (all_states=1 OR region_iso=?)",params)

def get_density(conn, params):
    return conn.execute("SELECT density as density_score FROM opencell_density WHERE \
        latitude = ROUND(?,1) AND longitude = ROUND(?,1)",params)

# Extract key weather info
def clean_weather(weather_json):
    cleaned_weather = {'description': weather_json['daily'][0]['weather'][0]['description'],'temperature': weather_json['daily'][0]['temp']['day']}
    return cleaned_weather