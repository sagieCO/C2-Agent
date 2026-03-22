import socket
from threading import Thread
import sqlite3
import json
import hashlib 

def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

def check_auth(sock_client, agent_info_json):
    data = json.loads(agent_info_json)
    name = data["name"]
    conn = sqlite3.connect('db.sql')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM agents WHERE agent_name = ?', (name,))
    result = cursor.fetchone() 
    
    if result:
        password_in_db = result[3] 
        if password_in_db == hash_password(data["password"]):
            conn.close()
            return True            
    return False

def handle_request(sock_client,agent_info):
    if check_auth(sock_client,agent_info):
        sock_client.send(b"Authentication passed successfully")
    else:
        sock_client.send(b"error in Authentication")

def add_agent_db(name, password, ip_address):
    
    hash_pass = hash_password(password)
    connection =sqlite3.connect("db.sql")
    curser = connection.cursor()

    try:
        curser.execute(""""
        INSERT INTO agents (agent_name,password_hash,ip,status)
        VALUE (?,?,?,?)""",(name,hash_pass,ip_address,'ONLINE'))
        connection.commit() 
        print(f"Successfully registered new agent: {name}")
        return True
    except sqlite3.IntegrityError:
        print(f"error - agent {name} is already exits")
        return False
    finally:
        connection.close()
if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.bind(('0.0.0.0',22))
    sock.listen(1)
    print("The server is ready for agents")
    while True:
        sock_client, addr_client = sock.accept()
        print(f'new connection for {addr_client} on port 22')
        foramt_auth = {"name": " ", "password": " "}
        sock_client.send(str(foramt_auth).encode())

        agent_info = sock_client.recv(2024).decode()#recive info to auth in DB

        Thread(target=handle_request,args=(sock_client,agent_info),daemon=True).start()# creat thread for every agent


    

