import socket
import threading
import os

CACHE_DIR = './cache'
SERVER_IP = '192.168.16.18'
SERVER_PORT = 9999

if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

def handle_client(client_socket):
    try:
        file_name = client_socket.recv(1024).decode()
        if file_name:
            cache_file_path = os.path.join(CACHE_DIR, file_name)

            # Check if file is already in cache
            if os.path.exists(cache_file_path):
                client_socket.send(b"FileFound")
                with open(cache_file_path, 'rb') as f:
                    while (chunk := f.read(1024)):
                        client_socket.send(chunk)  # Send cached file to client
                client_socket.send(b"<EOF>")  # Send EOF marker after file transfer
                print(f"[INFO] Sent file '{file_name}' from cache to client.")
            else:
                # Request file from server if not in cache
                print(f"[INFO] File '{file_name}' not found in CDN cache. Requesting from server...")
                request_from_server(file_name, client_socket)
        else:
            client_socket.send(b"InvalidRequest")
    finally:
        client_socket.close()

def request_from_server(file_name, client_socket):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        try:
            print(f"[INFO] Requesting file '{file_name}' from server...")
            server_socket.connect((SERVER_IP, SERVER_PORT))
            server_socket.send(file_name.encode())

            # Read status response from server
            response = server_socket.recv(1024)
            if response == b"FileFound":
                print(f"[INFO] File '{file_name}' found on server. Preparing to download...")

                # Send acknowledgment to start file transfer
                server_socket.send(b"StartTransfer")

                # Write the incoming file data to cache
                cache_file_path = os.path.join(CACHE_DIR, file_name)
                with open(cache_file_path, 'wb') as f:
                    while True:
                        data = server_socket.recv(1024)
                        if data.endswith(b"<EOF>"):
                            f.write(data[:-5])  # Write data excluding the EOF marker
                            break
                        f.write(data)
                
                print(f"[INFO] File '{file_name}' downloaded from server and cached.")
                handle_file_send_to_client(file_name, client_socket)
            else:
                client_socket.send(b"FileNotFound")
                print(f"[ERROR] File '{file_name}' not found on server.")
        except (ConnectionError, TimeoutError) as e:
            print(f"[ERROR] Could not connect to server: {e}")

def handle_file_send_to_client(file_name, client_socket):
    cache_file_path = os.path.join(CACHE_DIR, file_name)
    client_socket.send(b"FileFound")
    with open(cache_file_path, 'rb') as f:
        while (data := f.read(1024)):
            client_socket.send(data)
    client_socket.send(b"<EOF>")  # Send EOF marker after the file transfer
    print(f"[INFO] Sent file '{file_name}' from CDN cache to client.")

def start_cdn_peer():
    cdn_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cdn_socket.bind(("192.168.16.185", 8000))
    cdn_socket.listen(5)
    print("[INFO] CDN Peer listening for connections on port 8000...")

    while True:
        client_socket, _ = cdn_socket.accept()
        threading.Thread(target=handle_client, args=(client_socket,)).start()

if __name__ == "_main_":
    start_cdn_peer()