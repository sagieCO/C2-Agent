import socket
ip_server = '192.168.1.79'
port_server = 22






if __name__ == "__main__":
    
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.connect((ip_server,port_server))#connecting to server


    type_info = sock.recv(2024)
    type_input = input("")
    agent_info = sock.recv(1024).decode()#recive format of auth
    print(agent_info)
    agent_input = input("fill the fields")
    sock.send(agent_input.encode())#send info to check Auth

    info = sock.recv(2024).decode()
    print(info)#answer if passed DB

