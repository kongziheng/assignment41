import socket
import sys
import base64
import time
import os

MAX_RETRIES = 5
CHUNK_SIZE = 1000
def send_and_receive(sock, message, server_addr, timeout=1):
    sock.settimeout(timeout)
    for i in range(MAX_RETRIES):
        try:
            sock.sendto(message.encode(), server_addr)
            return sock.recvfrom(65536)
        except socket.timeout:
            print(f"[Retry] No response. Retrying {i+1}/{MAX_RETRIES}...")
            timeout *= 2
    raise TimeoutError("Max retries reached")
def download_file(filename, sock, server_addr):
    try:
        # Send DOWNLOAD request
        resp, _ = send_and_receive(sock, f"DOWNLOAD {filename}", server_addr)
        parts = resp.decode().split()

        if parts[0] == "ERR":
            print(f"[Client] File {filename} not found on server.")
            return

        size = int(parts[3])
        port = int(parts[5])
        print(f"[Client] Downloading '{filename}' ({size} bytes) from port {port}")
        # Create new socket for data transfer
        data_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        start = 0

        os.makedirs("client_files", exist_ok=True)
        local_path = os.path.join("client_files", filename)

        with open(local_path, "wb") as f:
            while start < size:
                end = min(start + CHUNK_SIZE - 1, size - 1)
                request = f"FILE {filename} GET START {start} END {end}"
                data_sock.settimeout(1)
                for attempt in range(MAX_RETRIES):
                    try:
                        data_sock.sendto(request.encode(), (server_addr[0], port))
                        data, _ = data_sock.recvfrom(65536)
                        decoded = data.decode()
                        if decoded.startswith("FILE") and "DATA" in decoded:
                            encoded_data = decoded.split("DATA ")[1]
                            chunk = base64.b64decode(encoded_data)
                            f.seek(start)
                            f.write(chunk)
                            print("*", end="", flush=True)
                            break
                    except socket.timeout:
                        continue
                start = end + 1
