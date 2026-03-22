import socket


ip_server = '192.168.1.79'

sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.connect()