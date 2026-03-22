import socket
import T
sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.bind(('0.0.0.0',22))

sock.accept(1)
