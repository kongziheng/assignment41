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
