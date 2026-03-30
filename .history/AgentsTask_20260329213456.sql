CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,   -- ID ייחודי למשימה
    agent_id INTEGER,                       -- לאיזה סוכן
    agent_name TEXT,                        -- נוח לדיבאג
    task_type TEXT NOT NULL,                -- whoami / processlist / screenshot וכו
    params TEXT,                            -- פרמטרים (למשל path לקובץ)
    status TEXT DEFAULT 'PENDING',          -- PENDING / SENT / DONE
    result TEXT,                            -- תשובת הסוכן
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (agent_id) REFERENCES agents(id)
);