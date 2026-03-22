import socket
from threading import Thread
import sqlite3
import json
import hashlib

def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

def init_db():
    conn = sqlite3.connect('db.sql')
    cursor = conn.cursor()
    
    try:
        # קריאת הקובץ החיצוני
        with open('D.sql', 'r') as f:
            sql_script = f.read()
        
        # הרצת הסקריפט
        cursor.executescript(sql_script)
        conn.commit()
        print("[+] Database initialized from schema.sql")
    except Exception as e:
        print(f"[x] Error initializing database: {e}")
    finally:
        conn.close()

def check_auth(name, password_raw):
    conn = sqlite3.connect('db.sql')
    cursor = conn.cursor()
    cursor.execute('SELECT password_hash FROM agents WHERE agent_name = ?', (name,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return result[0] == hash_password(password_raw)
    return False

def add_agent_db(name, password, ip_address):
    hashed_pw = hash_password(password)
    connection = sqlite3.connect("db.sql")
    cursor = connection.cursor()
    try:
        cursor.execute("""
            INSERT INTO agents (agent_name, password_hash, ip, status)
            VALUES (?, ?, ?, ?)""", (name, hashed_pw, ip_address, 'ONLINE'))
        connection.commit()
        print(f"Successfully registered new agent: {name}")
        return True
    except sqlite3.IntegrityError:
        print(f"Error - agent {name} already exists")
        return False
    finally:
        connection.close()

def handle_request(sock_client, agent_info_json, type_auth, addr_client):
    try:
        data = json.loads(agent_info_json)
        name = data.get("name")
        password = data.get("password")
        ip = addr_client[0] 

        if type_auth.lower() == 'login':
            if check_auth(name, password):
                sock_client.send(b"Authentication passed successfully")
            else:
                sock_client.send(b"Error in Authentication")

        elif type_auth.lower() == 'create':
            if add_agent_db(name, password, ip):
                sock_client.send(b"Agent created successfully")
            else:
                sock_client.send(b"Error: Agent already exists")
                
    except Exception as e:
        print(f"Error handling request: {e}")
    finally:
        sock_client.close() 

if __name__ == '__main__':
    init_db() 
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('0.0.0.0', 22))
    sock.listen(5)
    print("The server is ready for agents")
    
    while True:
        sock_client, addr_client = sock.accept()
        print(f'New connection from {addr_client}')

        sock_client.send(b"Login or Create agent")
        type_auth = sock_client.recv(1024).decode().strip()

        format_auth = {"name": " ", "password": " "}
        sock_client.send(json.dumps(format_auth).encode())
        
        agent_info = sock_client.recv(2024).decode()

        Thread(target=handle_request, args=(sock_client, agent_info, type_auth, addr_client), daemon=True).start()