import flask
from flask import Flask, request, jsonify
import json
import threading
import time
from datetime import datetime
import pandas as pd
from collections import defaultdict
import os

app = Flask(__name__)

# Global data storage
clients = {}
all_data = []
client_stats = defaultdict(list)
lock = threading.Lock()

@app.route('/api/register', methods=['POST'])
def register_client():
    data = request.json
    client_id = data.get('client_id')
    client_name = data.get('client_name', f'Client_{client_id}')
    
    with lock:
        clients[client_id] = {
            'name': client_name,
            'registered_at': datetime.now(),
            'last_seen': datetime.now(),
            'active': True,
            'test_count': 0
        }
    
    print(f"Client registered: {client_name} ({client_id})")
    return jsonify({'status': 'registered', 'client_id': client_id})

@app.route('/api/report', methods=['POST'])
def report_speed():
    data = request.json
    client_id = data.get('client_id')
    speed = data.get('speed')
    timestamp = data.get('timestamp', datetime.now().strftime("%H:%M:%S"))
    site = data.get('site', 'Unknown')
    
    with lock:
        # Update client last seen
        if client_id in clients:
            clients[client_id]['last_seen'] = datetime.now()
            clients[client_id]['active'] = True
            clients[client_id]['test_count'] += 1
        
        # Store data point
        data_point = {
            'client_id': client_id,
            'client_name': clients.get(client_id, {}).get('name', client_id),
            'speed': speed,
            'timestamp': timestamp,
            'site': site,
            'server_time': datetime.now().isoformat()
        }
        
        all_data.append(data_point)
        client_stats[client_id].append(data_point)
        
        print(f"Speed report: {clients.get(client_id, {}).get('name', client_id)} - {speed} Mbps")
    
    return jsonify({'status': 'recorded'})

@app.route('/api/clients')
def get_clients():
    with lock:
        # Mark inactive clients
        current_time = datetime.now()
        for client_id in clients:
            if (current_time - clients[client_id]['last_seen']).seconds > 30:
                clients[client_id]['active'] = False
        
        # Prepare client data
        dashboard_clients = []
        for client_id, client_info in clients.items():
            client_data = client_stats.get(client_id, [])
            speeds = [d['speed'] for d in client_data]
            
            dashboard_clients.append({
                'id': client_id,
                'name': client_info['name'],
                'active': client_info['active'],
                'last_seen': client_info['last_seen'].strftime("%H:%M:%S"),
                'test_count': client_info['test_count'],
                'avg_speed': sum(speeds) / len(speeds) if speeds else 0,
                'data': [{'time': d['timestamp'], 'speed': d['speed']} for d in client_data[-50:]]  # Last 50 points
            })
        
        # Calculate overall stats
        all_speeds = [d['speed'] for d in all_data]
        
        if not dashboard_clients:
            # Return empty structure if no clients
            return jsonify({
                'total_clients': 0,
                'active_clients': 0,
                'total_tests': 0,
                'avg_speed': 0,
                'clients': []
            })
        
        response_data = {
            'total_clients': len(clients),
            'active_clients': sum(1 for c in clients.values() if c['active']),
            'total_tests': len(all_data),
            'avg_speed': sum(all_speeds) / len(all_speeds) if all_speeds else 0,
            'clients': dashboard_clients
        }
        
        print(f"Sending data: {len(response_data['clients'])} clients, total: {response_data['total_clients']}")
        return jsonify(response_data)

@app.route('/api/export')
def export_data():
    with lock:
        # Convert to DataFrame for easy export
        df = pd.DataFrame(all_data)
        csv_data = df.to_csv(index=False)
        
        return csv_data, 200, {
            'Content-Type': 'text/csv',
            'Content-Disposition': 'attachment; filename=download_analysis.csv'
        }

def cleanup_inactive_clients():
    """Remove clients that haven't been seen for more than 5 minutes"""
    while True:
        time.sleep(60)  # Check every minute
        with lock:
            current_time = datetime.now()
            inactive_clients = [
                cid for cid, info in clients.items()
                if (current_time - info['last_seen']).seconds > 300
            ]
            for cid in inactive_clients:
                print(f"Removing inactive client: {clients[cid]['name']}")
                del clients[cid]
                if cid in client_stats:
                    del client_stats[cid]

if __name__ == '__main__':
    # Start cleanup thread
    cleanup_thread = threading.Thread(target=cleanup_inactive_clients, daemon=True)
    cleanup_thread.start()
    
    print("Simple Multi-Client Server")
    print("==========================")
    print("API Endpoints:")
    print("  POST /api/register - Register new client")
    print("  POST /api/report - Report speed test")
    print("  GET  /api/clients - Get all client data")
    print("  GET  /api/export - Export all data")
    print("\nStarting server on http://localhost:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
