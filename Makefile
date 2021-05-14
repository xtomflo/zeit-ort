# ETL for acquiring, transforming and storing Holidays, IP Address and OpenCellID data
SHELL := bash

.PHONY: create_holidays_table create_holiday_regions_table create_opencell_table
all:    .jq .json2csv load_holidays load_holiday_regions load_ip_locations

# Ensure JQ is installed
.jq:
	wget https://github.com/stedolan/jq/releases/download/jq-1.6/jq-linux64
	mv jq-linux64 jq
	chmod 777 jq
	touch $@
# Ensure json2csv is installed
.json2csv:
	wget https://github.com/jehiah/json2csv/releases/download/v1.2.1/json2csv-1.2.1.linux-amd64.go1.13.5.tar.gz
	tar -xzf json2csv-1.2.1.linux-amd64.go1.13.5.tar.gz 
	rm json2csv-1.2.1.linux-amd64.go1.13.5.tar.gz
	mv json2csv-1.2.1.linux-amd64.go1.13.5/json2csv .
	rmdir json2csv-1.2.1.linux-amd64.go1.13.5
	chmod 777 json2csv
	touch $@

# Get the list of countries in json
countries.json:
	curl "https://calendarific.com/api/v2/countries?api_key=c7f7787d4c0e5365332fae488a3a94af15e856ca" > $@    

# Convert the json with countries into an iterable list
countries.txt: countries.json
	cat countries.json | ./.jq '.response.countries[] | ."iso-3166"' -c | tr -d \" > $@
# Using the iterable list of countries get all holidays per country
holidays.json: countries.txt
	cat countries.txt | while read line ; do \
	curl "https://calendarific.com/api/v2/holidays?api_key=c7f7787d4c0e5365332fae488a3a94af15e856ca&country=$$line&type=national,local&year=2021" >> $@ ; \
	done ; \
# Transform holidays and add index
holidaysT.json: holidays.json
	cat holidays.json  | ./.jq '.response.holidays[] ' -c | ./.jq '-s' |  ./.jq 'def add_id(prefix): ( foreach .[] as $$o (0; . + 1; {"id": (prefix + tostring) } + $$o) ); add_id("")' > $@

# Flatten the holidays json and take needed elements, keep elements in { } for keys to remain
data/holidays.csv: holidaysT.json
	cat holidaysT.json | ./.jq '[paths(scalars) as $$path | {"key": $$path | join("_"), "value": getpath($$path)}] | from_entries | { id, name, country_id, country_name, date_iso, states }' -c | ./.json2csv -p=true -k id,name,country_id,country_name,date_iso,states > $@

# Holiday ID and region code as separate table for holidays affecting only specific regions within a country
data/holidayRegions.csv: holidaysT.json
	cat holidaysT.json | ./.jq 'select(.states != "All") | { id, "states": .states[].iso}' -c | ./.json2csv -p=true -k id,states > $@	

# Download OpenCellData
data/cell_towers.csv.gz:
	curl -O "https://opencellid.org/ocid/downloads?token=pk.3278cbbd75e56f5bec70803a2f4910fd&type=full&file=cell_towers.csv.gz" > $@

# Transform IP Ranges 
data/ip_geoname.csv:
	python3 python/ip-transform.py
# Generate IP to Location tables
data/ip_location.csv: data/ip_geoname.csv
	python3 python/geo_location.py

# Creating Tables 
create_holidays_table: holidays.csv
	sqlite3 db.sqlite < sql/create_holidays.sql 
create_holiday_regions_table: holidayRegions.csv
	sqlite3 db.sqlite < sql/create_holiday_regions.sql 
create_opencell_table: data/cell_towers.csv.gz
	sqlite3 db.sqlite < sql/opencell.sql
create_ip_locations_table: data/ip_location.csv
	sqlite3 db.sqlite < sql/ip_locations.sql

# Loading Data into Tables
load_opencell: create_opencell_table
	echo "Loading OpenCell"
	sqlite3 db.sqlite -cmd ".mode csv" ".import ../cell_towers.csv/cell_towers.csv opencell"
load_holidays: create_holidays_table holidays.csv
	echo "Loading holidays"
	sqlite3 db.sqlite -cmd ".mode csv" ".import holidays.csv holidays"
	echo "Loading holiday regions"
load_holiday_regions: create_holiday_regions_table
	sqlite3 db.sqlite -cmd ".mode csv" ".import holidayRegions.csv holiday_regions"
load_ip_locations: create_ip_locations_table
	sqlite3 db.sqlite -cmd ".mode csv" ".import data/ip_location.csv ip_locations"

nuke:
	rm *.txt
	rm *.json
	rm *.csv
	
