import socket
import threading
import os

MAX_CONNECTIONS = 4 
SERVER_PORT = 9999
CACHE_DIR = './data'
peers = []

CDN_PEER_IP = "172.20.10.4"
CDN_PEER_PORT = 8000  # Fixed port for CDN peer

def handle_client(client_socket, client_address):
    global peers
    print(f"[INFO] Connected with {client_address}")
    peers.append((client_address[0], client_address[1]))

    try:
        # Receive the requested file name from the client
        file_name = client_socket.recv(1024).decode()
        file_path = os.path.join(CACHE_DIR, file_name)
        
        if os.path.isfile(file_path):
            client_socket.send(b"FileFound")  # Send a separate "FileFound" status message
            # Wait for an acknowledgment to start sending the file
            ack = client_socket.recv(1024)
            if ack == b"StartTransfer":
                with open(file_path, 'rb') as f:
                    while (chunk := f.read(1024)):
                        client_socket.send(chunk)  # Send the file in chunks of 1024 bytes
                client_socket.send(b"<EOF>")  # Send EOF marker after file data

                print(f"[INFO] Sent file '{file_name}' to client.")
        else:
            client_socket.send(b"FileNotFound")  # Notify client if file is not found
            print(f"[ERROR] File '{file_name}' not found on server.")
    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")
    finally:
        client_socket.close()
        peers.remove((client_address[0], client_address[1]))
        print(f"[INFO] Updated peers list: {peers}")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("172.20.10.2", SERVER_PORT))
    server.listen(7)
    print(f"[INFO] Server listening on port {SERVER_PORT}")

    while True:
        client_socket, client_address = server.accept()

        # Debugging: Print active connections count
        print(f"[INFO] Active connections: {len(peers)}")

        print(f"IP: {client_address[0]}, Port: {client_address[1]}")
        # Check if the incoming connection is from the CDN peer
        if client_address[0] == CDN_PEER_IP or client_address[1] == CDN_PEER_PORT:
            print(f"[INFO] CDN peer connected. Allowing connection regardless of the limit.")
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.start()
        elif len(peers) >= MAX_CONNECTIONS:
            print(f"[INFO] Server limit reached. Directing {client_address} to CDN peer...")
            client_socket.send(b"RedirectToCDN")  # Inform client to connect to CDN
            client_socket.close()  # Close the connection with the client
        else:
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.start()
            print(f"[INFO] Active connections: {threading.active_count() - 1}")
            print(f"[INFO] Already Connected Peers: {peers}")

if __name__ == "__main__":
    start_server()
