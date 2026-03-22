import socket
ip_server = '192.168.1.79'
port_server = 22






if __name__ == "__main__":
    
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.connect((ip_server,port_server))#connecti

    agent_info = sock.recv(1024).decode()
    print(agent_info)
    agent_input = input("fill the fields")
    sock.send(agent_input.encode())