CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,   
    agent_id INTEGER,                       
    agent_name TEXT,                        
    task_type TEXT NOT NULL,                
    params TEXT,                            
    status TEXT DEFAULT 'PENDING',         
    result TEXT,                            
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (agent_id) REFERENCES agents(id)
);