CREATE TABLE IF NOT EXISTS agentsTask (
    agent_name TEXT NOT NULL,
    idTask INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_address TEXT,
    password_hash TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'OFFLINE'
);