import socket
from threading import Thread
import sqlite3

def check_auth(sock_client,addr_client):
    connection = splite3.connect('db.sql')
    




if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.bind(('0.0.0.0',22))
    print("The server is ready for agents")

    Thread(target=_,args=_,_ daemon=True).start()# creat thread for every agent
    sock_client, addr_client = sock.accept()
    print(f'new connection for {addr_client} on port 22')

