import requests
import socket

def test_connection():
    print("Testing connection to server...")
    
    # Test different server URLs
    urls = [
        "http://localhost:5000/api/clients",
        "http://127.0.0.1:5000/api/clients", 
        "http://172.20.225.22:5000/api/clients"
    ]
    
    for url in urls:
        print(f"\nTesting: {url}")
        try:
            response = requests.get(url, timeout=3)
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                print(f"  Success! Server is reachable at {url}")
                return url
        except Exception as e:
            print(f"  Failed: {e}")
    
    print("\nNo server connection found!")
    return None

def check_local_ip():
    print(f"\nYour local IP addresses:")
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"  Hostname: {hostname}")
        print(f"  Local IP: {local_ip}")
        
        # Get all network interfaces
        import psutil
        interfaces = psutil.net_if_addrs()
        for interface, addresses in interfaces.items():
            for addr in addresses:
                if addr.family == socket.AF_INET and not addr.address.startswith('127.'):
                    print(f"  {interface}: {addr.address}")
    except ImportError:
        print("  Install psutil to see all network interfaces: pip install psutil")
    except Exception as e:
        print(f"  Error getting IP: {e}")

if __name__ == "__main__":
    working_url = test_connection()
    check_local_ip()
    
    if working_url:
        print(f"\n=== USE THIS URL IN YOUR CLIENT: {working_url} ===")
    else:
        print("\n=== SERVER CONNECTION ISSUES FOUND ===")
        print("1. Make sure server is running")
        print("2. Check firewall settings")
        print("3. Try running server and client on same machine first")
