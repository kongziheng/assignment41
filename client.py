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
