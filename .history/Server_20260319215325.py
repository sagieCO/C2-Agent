import socket
import threading
import thread

sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.bind(('0.0.0.0',22))
print("The server is ready for agents")

client_socket, addr_client = sock.accept()
