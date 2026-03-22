import socket
import json

ip_server = '127.0.0.1' 
port_server = 22

if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((ip_server, port_server))

        msg = sock.recv(1024).decode()
        print(f"Server says: {msg}")
        choice = input("Your choice (Login/Create): ")
        sock.send(choice.encode())

        # 2. קבלת פורמט האימות
        format_msg = sock.recv(1024).decode()
        print(f"Fill the fields: {format_msg}")
        
        name = input("Enter Name: ")
        password = input("Enter Password: ")
        
        # בניית JSON מסודר במקום להקליד ידנית
        auth_data = json.dumps({"name": name, "password": password})
        sock.send(auth_data.encode())

        # 3. קבלת תשובת האימות הסופית
        final_answer = sock.recv(2024).decode()
        print(f"Final Status: {final_answer}")

    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        sock.close()