CREATE TABLE IF NOT EXISTS agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_name TEXT NOT NULL,
    ip_address TEXT,
    password_hash TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'OFFLINE'
);

CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,   
    agent_id INTEGER,                       
    agent_name TEXT,                        
    task_type TEXT NOT NULL,                
    params TEXT,                            
    status TEXT DEFAULT 'PENDING',         
    result TEXT,                            
    FOREIGN KEY (agent_id) REFERENCES agents(id)
);