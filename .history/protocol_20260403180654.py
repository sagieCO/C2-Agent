import uuid

def generate_task_id():
    return str(uuid.uuid4())
def create_task(task_id, command, args=None):
    return {
        "type": "task",
        "task_id": task_id,
        "command": command,
        "args": args or {}
    }
def create_result(task_id, status, result):
    return {
        "type": "result",
        "task_id": task_id,
        "status": status,
        "result": result
    }
def create_heartbeat(agent_id):
    return {
        "type": "heartbeat",
        "agent_id": agent_id
    }
def parse_message(msg):
    msg_type = msg.get("type")

    if msg_type == "task":
        return "task", msg
    elif msg_type == "result":
        return "result", msg
    elif msg_type == "heartbeat":
        return "heartbeat", msg
    else:
        return "unknown", msg