import socket
import threading
import thread

sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.bind(('0.0.0.0',22))
sock.listen(1)
sock.accept()
