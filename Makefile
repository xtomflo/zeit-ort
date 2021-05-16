# ETL for acquiring, transforming and storing Holidays, IP Address and OpenCellID data
SHELL := bash

include secrets.mk

.PHONY: create_holidays_table create_holiday_regions_table create_opencell_table
all:    .jq .json2csv load_holidays load_holiday_regions load_ip_locations

# TOOLS
# ---------------------------------------------------------------
# Ensure JQ is installed
.jq:
	wget https://github.com/stedolan/jq/releases/download/jq-1.6/jq-linux64
	mv jq-linux64 .jq
	chmod 777 .jq
	touch $@
# Ensure json2csv is installed
.json2csv:
	wget https://github.com/jehiah/json2csv/releases/download/v1.2.1/json2csv-1.2.1.linux-amd64.go1.13.5.tar.gz
	tar -xzf json2csv-1.2.1.linux-amd64.go1.13.5.tar.gz 
	rm json2csv-1.2.1.linux-amd64.go1.13.5.tar.gz
	mv json2csv-1.2.1.linux-amd64.go1.13.5/json2csv .json2csv
	rmdir json2csv-1.2.1.linux-amd64.go1.13.5
	chmod 777 .json2csv
	touch $@

# Create data folder if it doesn't exist
data: 
	mkdir data
# Holidays Data
# ---------------------------------------------------------------
# Get the list of countries in json
data/countries.json:
	curl "https://calendarific.com/api/v2/countries?api_key=$(CALENDARIFIC_KEY)" > $@
# Convert the json with countries into an iterable list
data/countries.txt: data/countries.json
	cat data/countries.json | ./.jq '.response.countries[] | ."iso-3166"' -c | tr -d \" > $@
# Using the iterable list of countries get all holidays per country
data/holidays.json: data/countries.txt
	cat data/countries.txt | while read line ; do \
	curl "https://calendarific.com/api/v2/holidays?api_key=$(CALENDARIFIC_KEY)&country=$$line&type=national,local&year=2021" >> $@ ; \
	done ; \
# Transform holidays and add index
data/holidaysT.json: data/holidays.json
	cat data/holidays.json  | ./.jq '.response.holidays[] ' -c | ./.jq '-s' |  ./.jq 'def add_id(prefix): ( foreach .[] as $$o (0; . + 1; {"id": (prefix + tostring) } + $$o) ); add_id("")' > $@
# Flatten the holidays json and take needed elements, keep elements in { } for keys to remain
data/holidays.csv: data/holidaysT.json
	cat data/holidaysT.json | ./.jq '[paths(scalars) as $$path | {"key": $$path | join("_"), "value": getpath($$path)}] | from_entries | { id, name, country_id, country_name, date_iso, states }' -c | ./.json2csv -p=true -k id,name,country_id,country_name,date_iso,states > $@

# Holiday ID and region code as separate table for holidays affecting only specific regions within a country
data/holidayRegions.csv: data/holidaysT.json
	cat data/holidaysT.json | ./.jq 'select(.states != "All") | { id, "states": .states[].iso}' -c | ./.json2csv -p=true -k id,states > $@	

# OpenCell Data
# ---------------------------------------------------------------
# Download OpenCellData
data/cell_towers.csv.gz:
	wget -O data/cell_towers.csv.gz "https://opencellid.org/ocid/downloads?token=$(OPENCELL_KEY)&type=full&file=cell_towers.csv.gz" > $@

# IP to Location Data
# ---------------------------------------------------------------
# Get IP to Location Data
data/GeoLite.zip:
	wget -O data/GeoLite.zip "https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-City-CSV&license_key=$(GEOLITE_KEY)&suffix=zip"
	unzip data/GeoLite.zip -d data/

# Transform IP Ranges 
data/ip_geoname.csv: data/GeoLite.zip
	cp data/GeoLite2-City*/GeoLite2-City-Blocks-IPv4.csv data/
	python3 python/ip-transform.py 
# Generate IP to Location tables
data/ip_location.csv: data/ip_geoname.csv
	cp data/GeoLite2-City*/GeoLite2-City-Locations-en.csv data/
	python3 python/geo_location.py 

# Database & Loading
# ---------------------------------------------------------------
# Create database
zeit-ort.db:
	sqlite3 zeit-ort.db "VACUUM;"

# Creating Tables 
create_holidays_table: zeit-ort.db data/holidays.csv
	sqlite3 zeit-ort.db < sql/create_holidays.sql 
create_holiday_regions_table: zeit-ort.db data/holidayRegions.csv
	sqlite3 zeit-ort.db < sql/create_holiday_regions.sql 
create_opencell_table: zeit-ort.db data/cell_towers.csv.gz
	sqlite3 zeit-ort.db < sql/opencell.sql
create_ip_locations_table: zeit-ort.db data/ip_location.csv
	sqlite3 zeit-ort.db < sql/ip_locations.sql

# Loading Data into Tables
load_opencell: create_opencell_table
	echo "Loading OpenCell"
	sqlite3 zeit-ort.db -cmd ".mode csv" ".import ../cell_towers.csv/cell_towers.csv opencell"
load_holidays: create_holidays_table 
	echo "Loading holidays"
	sqlite3 zeit-ort.db -cmd ".mode csv" ".import data/holidays.csv holidays"
	echo "Loading holiday regions"
load_holiday_regions: create_holiday_regions_table
	sqlite3 zeit-ort.db -cmd ".mode csv" ".import data/holidayRegions.csv holiday_regions"
load_ip_locations: create_ip_locations_table
	sqlite3 zeit-ort.db -cmd ".mode csv" ".import data/ip_location.csv ip_locations"

nuke:
	rm *.txt
	rm *.json
	rm *.csv
	

