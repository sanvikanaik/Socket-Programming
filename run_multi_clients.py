import subprocess
import sys
import time
import threading
import webbrowser
from tkinter import Tk, messagebox
import requests

def check_server_running():
    """Check if the server is already running"""
    try:
        response = requests.get("http://localhost:5000/api/clients", timeout=2)
        return response.status_code == 200
    except:
        return False

def start_server():
    """Start the multi-client server"""
    print("Starting Multi-Client Server...")
    try:
        subprocess.run([sys.executable, "multi_client_server.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Server error: {e}")
        messagebox.showerror("Server Error", f"Failed to start server: {e}")
    except KeyboardInterrupt:
        print("\nServer stopped by user")

def start_client():
    """Start a client instance"""
    print("Starting Multi-Client Analyzer...")
    try:
        subprocess.run([sys.executable, "multi_client_analyzer.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Client error: {e}")
        messagebox.showerror("Client Error", f"Failed to start client: {e}")

def main():
    print("=" * 60)
    print("Multi-Client Download Analyzer Launcher")
    print("=" * 60)
    
    # Check if server is already running
    if check_server_running():
        print("Server is already running!")
        choice = input("Do you want to:\n1. Start a new client\n2. Restart server\n3. Open dashboard\nChoice (1-3): ")
        
        if choice == "1":
            start_client()
        elif choice == "2":
            print("Please stop the running server first, then restart this launcher.")
        elif choice == "3":
            webbrowser.open("http://localhost:5000")
            print("Dashboard opened in browser")
        else:
            start_client()
    else:
        print("Server not running. Starting server...")
        print("The server will start in the background.")
        print("Then a client window will open.")
        print("You can open additional clients by running this script again.")
        
        # Start server in background thread
        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()
        
        # Wait for server to start
        print("Waiting for server to start...")
        for i in range(10):
            time.sleep(1)
            if check_server_running():
                print("Server started successfully!")
                break
        else:
            print("Server failed to start within 10 seconds")
            return
        
        # Open dashboard
        time.sleep(2)
        webbrowser.open("http://localhost:5000")
        print("Dashboard opened in browser")
        
        # Start client
        time.sleep(1)
        start_client()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nLauncher stopped by user")
    except Exception as e:
        print(f"Launcher error: {e}")
        messagebox.showerror("Launcher Error", f"An error occurred: {e}")
