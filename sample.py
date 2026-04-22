import requests
import time
import certifi
import socket
from datetime import datetime

# --- SETTINGS ---
SERVER_IP = "172.20.225.8"  # The IP from your screenshot
CLIENT_NAME = "Laptop_67"    # <-- CHANGE THIS ON EACH LAPTOP
FILE_URL = "https://speed.cloudflare.com/__down?bytes=10485760"

def download_and_measure():
    try:
        socket.gethostbyname("speed.cloudflare.com")
        start = time.time()
        r = requests.get(FILE_URL, stream=True, timeout=30, verify=certifi.where())
        size = 0
        for chunk in r.iter_content(chunk_size=1024*1024):
            if chunk: size += len(chunk)
        duration = time.time() - start
        return round((size * 8) / (1024 * 1024 * duration), 2)
    except: return 0

def send(speed):
    try:
        payload = {"client_id": CLIENT_NAME, "speed": speed, "timestamp": datetime.now().strftime("%H:%M:%S")}
        requests.post(f"http://{SERVER_IP}:5000/report", json=payload, timeout=5)
    except Exception as e: print(f"Error: {e}")

if __name__ == "__main__":
    print(f"Starting {CLIENT_NAME}...")
    for i in range(24):
        mbps = download_and_measure()
        send(mbps)
        print(f"Sample {i+1}: {mbps} Mbps sent.")
        time.sleep(10)
