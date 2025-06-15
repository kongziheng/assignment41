# server/UDPserver.py
import socket
import threading
import base64
import sys
import os
import random
def handle_client(addr, filename, server_port):
    try:
        filepath = os.path.join("server_files", filename)
        if not os.path.exists(filepath):
            err_msg = f"ERR {filename} NOT_FOUND"
            server.sendto(err_msg.encode(), addr)
            return
        filesize = os.path.getsize(filepath)
        transfer_port = random.randint(50000, 51000)
        server.sendto(f"OK {filename} SIZE {filesize} PORT {transfer_port}".encode(), addr)

        data_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        data_socket.bind(('', transfer_port))
        with open(filepath, "rb") as f:
            received = set()
            while True:
                req, client = data_socket.recvfrom(2048)
                msg = req.decode()
                if msg.startswith(f"FILE {filename} GET"):
                    parts = msg.split()
                    start = int(parts[5])
                    end = int(parts[7])
                    if (start, end) in received:
                        continue
                    f.seek(start)
                    chunk = f.read(end - start + 1)
                    encoded = base64.b64encode(chunk).decode()
                    reply = f"FILE {filename} OK START {start} END {end} DATA {encoded}"
                    data_socket.sendto(reply.encode(), client)
                    received.add((start, end))
                elif msg.strip() == f"FILE {filename} CLOSE":
                    data_socket.sendto(f"FILE {filename} CLOSE_OK".encode(), client)
                    break
        data_socket.close()
    except Exception as e:
        print(f"[Error] {e}")
