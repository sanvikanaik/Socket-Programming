import flask
from flask import Flask, request, jsonify, render_template_string
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

# HTML Template for Web Dashboard
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Multi-Client Download Analyzer Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .chart-container { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .client-list { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .client-item { display: flex; justify-content: space-between; align-items: center; padding: 10px; border-bottom: 1px solid #eee; }
        .status-online { color: #27ae60; font-weight: bold; }
        .status-offline { color: #e74c3c; font-weight: bold; }
        h1, h2 { margin: 0 0 15px 0; }
        .stat-value { font-size: 24px; font-weight: bold; color: #2c3e50; }
        .stat-label { color: #7f8c8d; font-size: 14px; }
        canvas { max-height: 400px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Multi-Client Download Analyzer Dashboard</h1>
        <p>Real-time monitoring of download speeds across multiple clients</p>
    </div>

    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-label">Total Clients</div>
            <div class="stat-value" id="total-clients">0</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Active Clients</div>
            <div class="stat-value" id="active-clients">0</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Total Tests</div>
            <div class="stat-value" id="total-tests">0</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Average Speed</div>
            <div class="stat-value" id="avg-speed">0 Mbps</div>
        </div>
    </div>

    <div class="chart-container">
        <h2>Speed Comparison Over Time</h2>
        <canvas id="speedChart"></canvas>
    </div>

    <div class="chart-container">
        <h2>Speed Distribution</h2>
        <canvas id="distributionChart"></canvas>
    </div>

    <div class="client-list">
        <h2>Connected Clients</h2>
        <div id="client-list-container"></div>
    </div>

    <script>
        let speedChart, distributionChart;
        
        function initCharts() {
            speedChart = new Chart(document.getElementById('speedChart'), {
                type: 'line',
                data: {
                    datasets: []
                },
                options: {
                    responsive: true,
                    scales: {
                        x: { title: { display: true, text: 'Time' } },
                        y: { title: { display: true, text: 'Speed (Mbps)' } }
                    }
                }
            });

            distributionChart = new Chart(document.getElementById('distributionChart'), {
                type: 'bar',
                data: {
                    labels: [],
                    datasets: []
                },
                options: {
                    responsive: true,
                    scales: {
                        y: { title: { display: true, text: 'Frequency' } }
                    }
                }
            });
        }

        function updateDashboard() {
            fetch('/api/dashboard')
                .then(response => response.json())
                .then(data => {
                    updateStats(data);
                    updateCharts(data);
                    updateClientList(data);
                });
        }

        function updateStats(data) {
            document.getElementById('total-clients').textContent = data.total_clients;
            document.getElementById('active-clients').textContent = data.active_clients;
            document.getElementById('total-tests').textContent = data.total_tests;
            document.getElementById('avg-speed').textContent = data.avg_speed.toFixed(2) + ' Mbps';
        }

        function updateCharts(data) {
            // Update speed chart
            const colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c'];
            speedChart.data.datasets = data.clients.map((client, index) => ({
                label: client.name,
                data: client.data.map(d => ({x: d.time, y: d.speed})),
                borderColor: colors[index % colors.length],
                backgroundColor: colors[index % colors.length] + '33',
                tension: 0.1
            }));
            speedChart.update();

            // Update distribution chart
            const allSpeeds = data.clients.flatMap(c => c.data.map(d => d.speed));
            const bins = [0, 10, 20, 30, 40, 50, 100, 200];
            const distribution = bins.map((bin, i) => {
                if (i === bins.length - 1) return 0;
                return allSpeeds.filter(s => s >= bin && s < bins[i + 1]).length;
            });

            distributionChart.data.labels = bins.slice(0, -1).map((b, i) => `${b}-${bins[i+1]} Mbps`);
            distributionChart.data.datasets = [{
                label: 'Speed Distribution',
                data: distribution,
                backgroundColor: '#3498db'
            }];
            distributionChart.update();
        }

        function updateClientList(data) {
            const container = document.getElementById('client-list-container');
            container.innerHTML = data.clients.map(client => `
                <div class="client-item">
                    <div>
                        <strong>${client.name}</strong>
                        <br>
                        <small>Last seen: ${client.last_seen}</small>
                        <br>
                        <small>Tests: ${client.test_count} | Avg: ${client.avg_speed.toFixed(2)} Mbps</small>
                    </div>
                    <div class="${client.active ? 'status-online' : 'status-offline'}">
                        ${client.active ? 'ONLINE' : 'OFFLINE'}
                    </div>
                </div>
            `).join('');
        }

        // Initialize and start updates
        initCharts();
        updateDashboard();
        setInterval(updateDashboard, 2000);
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_TEMPLATE)

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
    
    return jsonify({'status': 'recorded'})

@app.route('/api/dashboard')
def get_dashboard_data():
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
                'name': client_info['name'],
                'active': client_info['active'],
                'last_seen': client_info['last_seen'].strftime("%H:%M:%S"),
                'test_count': client_info['test_count'],
                'avg_speed': sum(speeds) / len(speeds) if speeds else 0,
                'data': [{'time': d['timestamp'], 'speed': d['speed']} for d in client_data[-20:]]  # Last 20 points
            })
        
        # Calculate overall stats
        all_speeds = [d['speed'] for d in all_data]
        
        return jsonify({
            'total_clients': len(clients),
            'active_clients': sum(1 for c in clients.values() if c['active']),
            'total_tests': len(all_data),
            'avg_speed': sum(all_speeds) / len(all_speeds) if all_speeds else 0,
            'clients': dashboard_clients
        })

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

@app.route('/api/clients')
def get_clients():
    with lock:
        return jsonify({
            'clients': [
                {
                    'id': cid,
                    'name': info['name'],
                    'active': info['active'],
                    'last_seen': info['last_seen'].isoformat(),
                    'test_count': info['test_count']
                }
                for cid, info in clients.items()
            ]
        })

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
                del clients[cid]
                if cid in client_stats:
                    del client_stats[cid]

if __name__ == '__main__':
    # Start cleanup thread
    cleanup_thread = threading.Thread(target=cleanup_inactive_clients, daemon=True)
    cleanup_thread.start()
    
    print("Multi-Client Download Analyzer Server")
    print("=====================================")
    print("Dashboard: http://localhost:5000")
    print("API Endpoints:")
    print("  POST /api/register - Register new client")
    print("  POST /api/report - Report speed test")
    print("  GET  /api/dashboard - Get dashboard data")
    print("  GET  /api/export - Export all data")
    print("  GET  /api/clients - List all clients")
    print("\nStarting server...")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
