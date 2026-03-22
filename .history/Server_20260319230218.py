import socket
from threading import Thread
import sqlite3

def check_auth(sock_client,addr_client):
    connection = sqlite3.connect('db.sql')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM agents WHERE agent_name = ?',)




if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.bind(('0.0.0.0',22))
    sock.listen(1)
    print("The server is ready for agents")

    Thread(target=_,args=_,_ daemon=True).start()# creat thread for every agent
    sock_client, addr_client = sock.accept()
    agent_info = {"name": "", "password": "123"}
    sock_client.send(str(agent_info).encode())
    print(f'new connection for {addr_client} on port 22')

