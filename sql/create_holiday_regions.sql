CREATE TABLE IF NOT EXISTS holiday_regions (
	id INTEGER,
	states TEXT
);

CREATE INDEX IF NOT EXISTS i_id
ON holiday_regions(id);


