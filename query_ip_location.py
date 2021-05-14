#
# Script enables querying IP to Location database ie. finding the location for a specific IP Address.   
# python3 query_ip_location.py [IP_ADDRESS]  for ex. python3 query_ip_location.py 91.64.108.237
#
import sqlite3
from ipaddress import ip_address
import sys

def create_connection(db_file): 
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

def get_location_for_ip(conn, ip_address):
    """
    Query tasks by priority
    :param conn: the Connection object
    :param priority:
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT country_iso_code, subdivision_1_iso_code, subdivision_1_name, city_name \
     FROM ip_locations_ip_index WHERE ? BETWEEN ip_range_start AND ip_range_end LIMIT 1;", (ip_address,))

    rows = cur.fetchall()

    for row in rows:
        print(row)

def main():
    database = "db.sqlite"
    # Get the IP address from input
    ip_addr = ip_address(sys.argv[1])
    # Convert IP address to INT
    ip_addr = int(ip_addr)
    # create a database connection
    conn = create_connection(database)

    with conn:
        get_location_for_ip(conn, ip_addr)

if __name__ == '__main__':
    main()