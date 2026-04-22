import requests
import json
import uuid

# Test client registration
def test_registration():
    try:
        # Register a test client
        client_id = str(uuid.uuid4())[:8]
        client_name = f"Test_Client_{client_id}"
        
        print(f"Registering client: {client_name}")
        
        register_response = requests.post(
            "http://172.20.225.22:5000/api/register",
            json={
                'client_id': client_id,
                'client_name': client_name
            },
            timeout=5
        )
        
        print(f"Registration status: {register_response.status_code}")
        print(f"Registration response: {register_response.text}")
        
        # Now check clients
        clients_response = requests.get("http://172.20.225.22:5000/api/clients", timeout=5)
        print(f"Clients status: {clients_response.status_code}")
        print(f"Clients response: {clients_response.text}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_registration()
