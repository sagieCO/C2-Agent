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
