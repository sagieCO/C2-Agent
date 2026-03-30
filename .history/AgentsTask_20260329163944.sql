CREATE TABLE IF NOT EXISTS agents_Task (
    agent_name TEXT NOT NULL,
    id_task INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_address TEXT,
task    status TEXT NOT NULL DEFAULT 'OFFLINE'
);