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