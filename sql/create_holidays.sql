CREATE TABLE IF NOT EXISTS holidays (
	name TEXT,
	country_id VARCHAR(2),
	country_name TEXT,
	date_iso DATETIME,
	locations TEXT,
	states TEXT,
	type_0 TEXT,
	type_1 TEXT
);

CREATE INDEX IF NOT EXISTS i_date_iso
ON holidays(date_iso);
