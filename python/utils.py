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

def wrap_period(period):
    return "+{} days".format(period)

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
