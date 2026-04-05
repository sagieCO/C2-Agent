import uuid
import json
import base64
def generate_task_id():
    return str(uuid.uuid4())
def recv_message(sock):
    header = sock.recv(10).decode().strip()
    if not header:
        return None
    
    total_size = int(header)
    data = b""
    
    while len(data) < total_size:
        chunk = sock.recv(4096)
        if not chunk:
            break
        data += chunk

    return json.loads(data.decode())
def send_message(sock_client, action):
    if isinstance(action, dict) and "result" in action:
        if isinstance(action["result"], bytes):
            action["result"] = base64.b64encode(action["result"]).decode()

    msg_bytes = json.dumps(action).encode()
    header = f"{len(msg_bytes):<10}".encode()
    sock_client.sendall(header + msg_bytes)
def create_heartbeat(agent_id):
    return {
        "type": "heartbeat",
        "agent_id": agent_id
    }
def create_task(task_id, command, args=None):
    return {
        "type": "task",
        "task_id": task_id,
        "command": command,
        "args": args or {}
    }
def create_result(task_id,command, status, result):
    return {
        "type": "result",
        "task_id": task_id,
        "command":command,
        "status": status,
        "result": result
    }
def create_ping(agent_id):
    
