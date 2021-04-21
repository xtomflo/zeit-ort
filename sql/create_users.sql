CREATE TABLE IF NOT EXISTS users (
        id INTEGER,
        email TEXT,
        password TEXT,
        name TEXT,
        address TEXT,
        user_state TEXT,
        created_at INTEGER,
        updated_at INTEGER,
        deleted_at INTEGER );
CREATE INDEX i_u_updated_at
ON users(updated_at);
