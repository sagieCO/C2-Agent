import sqlite3
import hashlib
import time
def init_db():
    db_file = 'db.sql' 
    schema_file = 'schema.sql'
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    try:
        with open(schema_file, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        cursor.executescript(sql_script)
        conn.commit()
        print(f"[+] Database '{db_file}' initialized using '{schema_file}'")
    except FileNotFoundError:
        print(f"[x] Error: Please create a file named '{schema_file}' in the same folder!")
    except Exception as e:
        print(f"[x] Error: {e}")
    finally:
        conn.close()
def check_auth(name, password_raw):
    conn = sqlite3.connect('db.sql')
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT id, password_hash FROM agents WHERE agent_name = ?', (name,))
        result = cursor.fetchone()
        if result:
            agent_id, pw_hash = result
            if pw_hash == hash_password(password_raw):
                cursor.execute(
                    "UPDATE agents SET status=? WHERE id=?", ("ONLINE", agent_id)
                )
                conn.commit()
                return True
        return False
    finally:
        conn.close()
def add_agent_db(name, password, ip_address):
    hash_pw = hash_password(password)
    connection = sqlite3.connect("db.sql")
    cursor = connection.cursor()
    try:
        cursor.execute("""
            INSERT INTO agents (agent_name, password_hash, ip_address, status)
            VALUES (?, ?, ?, ?)""", (name, hash_pw, ip_address, 'ONLINE'))
        connection.commit()
        print(f"Successfully registered new agent: {name}")
        return True
    except sqlite3.IntegrityError:
        print(f"Error - agent {name} already exists")
        return False
    finally:
        connection.close()




def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()
def get_agent_id(agent_name):
    conn = sqlite3.connect("db.sql")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM agents WHERE agent_name = ?", (agent_name,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0]  
    return None

def update_ping(agent_id):
    conn = sqlite3.connect("db.sql")
    cursor = conn.cursor()
    timestamp = time.time()
    cursor.execute(
        "UPDATE agents SET status=?, last_seen=? WHERE id=?",
        ("ONLINE", timestamp, agent_id)
    )
    conn.commit()
    conn.close()

def update_status(status):
    conn = sqlite3.connect("db.sql")
    cursor=
    if not status:
