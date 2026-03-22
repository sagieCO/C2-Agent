import socket


ip_server = '192.168.1.79'
port_server = 22
sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.connect((ip_server,port_server))

agent_info = recv(1024).decode()