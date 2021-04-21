CREATE TABLE IF NOT EXISTS holidays (
	name TEXT,
	country_id TEXT,
	country_name TEXT,
	date_iso INTEGER,
	type_0 TEXT,
	locations TEXT
);

CREATE INDEX IF NOT EXISTS i_date_iso
ON holidays(date_iso);
