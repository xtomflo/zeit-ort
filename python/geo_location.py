import pandas as pd

# Load Geoname to Location mapping
geoname_location = pd.read_csv("../IP2Geo/GeoLite2-City-Locations-en.csv")
# Filter for needed columns
geoname_location = geoname_location[['geoname_id','country_iso_code','subdivision_1_iso_code','subdivision_1_name','city_name']]
# Load IP to Geoname mapping
ip_geoname = pd.read_csv('data/ip_geoname.csv')
# Merge Dataframes on geoname
ip_location = pd.merge(ip_geoname, geoname_location, on="geoname_id")
# Save IP to Location mapping
ip_location.to_csv('data/ip_location.csv', index=False)

