CREATE TABLE IF NOT EXISTS holidays (
	id INTEGER,
	name TEXT,
	country_id VARCHAR(2),
	country_name TEXT,
	date_iso DATETIME,
	states TEXT
);

CREATE INDEX IF NOT EXISTS i_date_iso
ON holidays(date_iso);


