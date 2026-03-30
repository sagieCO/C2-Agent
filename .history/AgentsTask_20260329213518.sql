CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,   
    agent_id INTEGER,                       
    agent_name TEXT,                        
    task_type TEXT NOT NULL,                
    params TEXT,                            -- פרמטרים (למשל path לקובץ)
    status TEXT DEFAULT 'PENDING',          -- PENDING / SENT / DONE
    result TEXT,                            -- תשובת הסוכן
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (agent_id) REFERENCES agents(id)
);