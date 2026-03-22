import socket
import json
import subprocess
import os
import psutil

ip_server = '192.168.1.66' 
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

def get_whoami(command):

    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
            
        return output
            
    except Exception as e:
        return str(e).encode()
    
def get_file(file_path):
    try:
        # בדיקה אם הקובץ קיים לפני שמנסים לפתוח
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                return f.read() # מחזיר את כל תוכן הקובץ כבייטים
        else:
            return f"Error: File '{file_path}' not found.".encode()
    except Exception as e:
        return f"Error reading file: {e}".encode()
def get_network_connections():
    # 1. הגדרה ראשונית עם "=" ולא "+="
    conn_str = f"{'Proto':<7} {'Local Address':<35} {'Remote Address':<35} {'Status':<15}\n"
    conn_str += "-" * 90 + "\n"
    
    try:
        connections = psutil.net_connections(kind='inet')
        
        # 2. לולאה על האובייקטים (ולא range)
        for conn in connections[:15]: 
            # לוקחים את הפרוטוקול (TCP/UDP)
            proto = "TCP" if conn.type == socket.SOCK_STREAM else "UDP"
            
            # כתובת מקומית תמיד קיימת
            l_addr = f"{conn.laddr.ip}:{conn.laddr.port}"
            
            # כתובת מרוחקת לא תמיד קיימת (למשל במצב LISTEN)
            if conn.raddr:
                r_addr = f"{conn.raddr.ip}:{conn.raddr.port}"
            else:
                r_addr = "N/A"
            
            conn_str += f"{proto:<7} {l_addr:<25} {r_addr:<25} {conn.status:<15}\n"
            
    except Exception as e:
        conn_str += f"Error: {e}\n"
        
    return conn_str.encode()
def handler_command(command):
    if command.strip().lower() == 'whoami':
        return get_whoami(command)
    elif command.strip().lower()=='process list':
        return get_process_list()
    elif command.strip().lower() == 'netstat':
        return get_network_connections()
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
                print(command_from_server)
                if command_from_server.lower() == 'exit':
                    break
                
                result = handler_command(command_from_server)
                data_length = len(result)
                header = f"{data_length:<10}".encode()
                sock.send(header)
                sock.send(result)

    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        sock.close()