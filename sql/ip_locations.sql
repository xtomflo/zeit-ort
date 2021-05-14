CREATE TABLE IF NOT EXISTS ip_locations (
	ip_range_start INTEGER,
	ip_range_end INTEGER,
	geoname_id INTEGER,
	latitude REAL,
	longitude REAL,
	accuracy_radius INTEGER,
	country_iso_code TEXT,
	subdivision_1_iso_code TEXT,
	subdivision_1_name TEXT,
	city_name TEXT
);