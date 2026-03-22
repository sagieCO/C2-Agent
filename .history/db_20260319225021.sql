-- בתוך קובץ DB.SQL
CREATE TABLE IF NOT EXISTS agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_name TEXT NOT NULL,
    ip_address TEXT,
    password_hash TEXT NOT NULL,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);