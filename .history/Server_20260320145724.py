import socket
from threading import Thread
import sqlite3
import json
import hash 

def check_auth(sock_client, agent_info_json):
    data = json.loads(agent_info_json)
    name = data["name"]
    
    conn = sqlite3.connect('db.sql')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM agents WHERE agent_name = ?', (name,))
    result = cursor.fetchone() 
    
    if result:
        password_in_db = result[3] 
        if password_in_db == data[pass]




if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.bind(('0.0.0.0',22))
    sock.listen(1)
    print("The server is ready for agents")

    sock_client, addr_client = sock.accept()
    print(f'new connection for {addr_client} on port 22')
    foramt_auth = {"name": " ", "password": " "}
    sock_client.send(str(foramt_auth).encode())

    agent_info = sock_client.recv(2024).decode()#recive info to auth in DB

    Thread(target=check_auth,args=(sock_client,agent_info),daemon=True).start()# creat thread for every agent


    

