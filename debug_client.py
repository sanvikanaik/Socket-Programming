import requests
import json

# Test server connection
def test_server_connection():
    try:
        response = requests.get("http://172.20.225.22:5000/api/clients", timeout=5)
        print(f"Server response status: {response.status_code}")
        print(f"Raw response: {response.text}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Parsed JSON: {json.dumps(data, indent=2)}")
                
                if 'total_clients' in data:
                    print(f"Connected clients: {data['total_clients']}")
                    print(f"Active clients: {data['active_clients']}")
                    print("Client details:")
                    for client in data['clients']:
                        print(f"  - {client['name']}: {client['test_count']} tests, {client['avg_speed']:.2f} avg speed")
                else:
                    print("Missing expected fields in response")
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    test_server_connection()
