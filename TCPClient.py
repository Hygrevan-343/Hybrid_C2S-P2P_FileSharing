import socket
import os

CACHE_DIR = './cache'
SERVER_IP = "172.20.10.2"
SERVER_PORT = 9998
CDN_PEER_IP = "172.20.10.4"
CDN_PEER_PORT = 8000

os.makedirs(CACHE_DIR, exist_ok=True)

def request_from_cdn(file_name):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cdn_socket:
        try:
            cdn_socket.connect((CDN_PEER_IP, CDN_PEER_PORT))
            cdn_socket.send(file_name.encode())  # Request file from CDN
            response = cdn_socket.recv(1024).decode(errors='ignore')  # Response from CDN

            if response == "FileFound":
                print(f"[INFO] File '{file_name}' found on CDN. Downloading...")
                cache_file_path = os.path.join(CACHE_DIR, file_name)
                with open(cache_file_path, 'wb') as f:  # Open file in binary mode
                    while True:
                        data = cdn_socket.recv(1024)
                        if not data or data == b"<EOF>":  # Check for EOF marker or empty data
                            break  # Stop if the EOF marker is received
                        f.write(data)
                print(f"[INFO] File '{file_name}' downloaded from CDN.")
            elif response == "FileNotFound":
                print(f"[ERROR] File '{file_name}' not found on CDN.")
            else:
                print(f"[ERROR] Unexpected response from CDN: {response}")
        except (ConnectionError, TimeoutError) as e:
            print(f"[ERROR] Could not connect to CDN: {e}")

def request_from_server(file_name):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        try:
            server_socket.connect((SERVER_IP, SERVER_PORT))
            server_socket.send(file_name.encode())  # Request file from server

            response = server_socket.recv(1024).decode(errors='ignore')  # Server response
            print(f"[INFO] Response from server: {response}")  # Log server response

            if response == "FileFound":
                print(f"[INFO] File '{file_name}' found on server. Downloading...")
                cache_file_path = os.path.join(CACHE_DIR, file_name)

                with open(cache_file_path, 'wb') as f:  # Open file in binary mode
                    while True:
                        data = server_socket.recv(1024)
                        if not data or data == b"<EOF>":  # Check for EOF marker or empty data
                            break  # Stop if the EOF marker is received
                        f.write(data)
                print(f"[INFO] File '{file_name}' downloaded from server.")
            elif response == "TrafficBusy":
                peers_data = server_socket.recv(1024).decode(errors='ignore')
                peers = eval(peers_data) if peers_data else []
                print("[INFO] Server busy. Attempting to connect to CDN...")
                request_from_cdn(file_name)
            elif response == "RedirectToCDN":
                print("[INFO] Server is busy. Connecting to CDN...")
                request_from_cdn(file_name)
            else:
                print(f"[ERROR] File '{file_name}' not found on server.")
        except (ConnectionError, TimeoutError) as e:
            print(f"[ERROR] Could not connect to server: {e}")

def main():
    while True:
        file_name = input("Enter the file name (with extension) to request or type 'close' to exit: ")
        if file_name.lower() == 'close':
            break
        if os.path.exists(os.path.join(CACHE_DIR, file_name)):
            print(f"[INFO] File '{file_name}' is available in cache.")
        else:
            request_from_server(file_name)

if __name__ == "__main__":
    main()
