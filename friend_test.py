import requests

def test_server_connection():
    print("Testing connection to your friend's server...")
    
    # Try different IP addresses
    urls_to_test = [
        "http://172.20.225.22:5000/api/clients",
        "http://localhost:5000/api/clients",  # Only if running on same machine
    ]
    
    for url in urls_to_test:
        print(f"\nTrying: {url}")
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"SUCCESS! Connected to server at: {url}")
                print("Use this URL in your client application!")
                return url
            else:
                print(f"Server responded with: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("Connection refused - server might be blocking connections")
        except requests.exceptions.Timeout:
            print("Connection timeout - network issue or wrong IP")
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n=== CONNECTION FAILED ===")
    print("Possible issues:")
    print("1. Wrong IP address")
    print("2. Firewall blocking connection")
    print("3. Server not accessible from your network")
    print("4. Different network/subnet")

if __name__ == "__main__":
    test_server_connection()
