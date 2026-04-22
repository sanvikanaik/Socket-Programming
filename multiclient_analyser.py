import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import requests
import time
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import json
import os
import uuid
import socket
from urllib.parse import urljoin, urlparse
import certifi
from bs4 import BeautifulSoup
import re

class MultiClientDownloadAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Client Download Analyzer")
        self.root.geometry("1400x900")
        
        # Client configuration
        self.client_id = str(uuid.uuid4())[:8]
        self.client_name = f"Client_{socket.gethostname()}_{self.client_id}"
        self.server_url = "http://localhost:5000"
        
        # Data storage
        self.local_data = []
        self.server_data = []
        self.all_clients = {}
        self.is_running = False
        self.is_connected = False
        
        # Test websites
        self.test_sites = [
            {"name": "Cloudflare", "url": "https://speed.cloudflare.com/__down?bytes=10485760"},
            {"name": "Fast.com", "url": "https://fast.com"},
            {"name": "Speedtest.net", "url": "https://www.speedtest.net"},
            {"name": "Google Drive", "url": "https://drive.google.com"},
            {"name": "Custom", "url": ""}
        ]
        
        self.setup_ui()
        self.register_with_server()
        self.start_sync_thread()
        
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Connection Panel
        conn_frame = ttk.LabelFrame(main_frame, text="Server Connection", padding="10")
        conn_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Server URL
        ttk.Label(conn_frame, text="Server URL:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.server_url_var = tk.StringVar(value=self.server_url)
        ttk.Entry(conn_frame, textvariable=self.server_url_var, width=40).grid(row=0, column=1, padx=(0, 10))
        
        # Client info
        ttk.Label(conn_frame, text="Client ID:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        ttk.Label(conn_frame, text=self.client_id, font=("Courier", 10, "bold")).grid(row=0, column=3, padx=(0, 10))
        
        ttk.Label(conn_frame, text="Client Name:").grid(row=0, column=4, sticky=tk.W, padx=(0, 10))
        self.client_name_var = tk.StringVar(value=self.client_name)
        ttk.Entry(conn_frame, textvariable=self.client_name_var, width=20).grid(row=0, column=5, padx=(0, 10))
        
        # Connection status
        self.conn_status_var = tk.StringVar(value="Connecting...")
        self.conn_status_label = ttk.Label(conn_frame, textvariable=self.conn_status_var, font=("Arial", 10, "bold"))
        self.conn_status_label.grid(row=0, column=6, padx=(10, 0))
        
        ttk.Button(conn_frame, text="Reconnect", command=self.register_with_server).grid(row=0, column=7, padx=(10, 0))
        
        # Control Panel
        control_frame = ttk.LabelFrame(main_frame, text="Control Panel", padding="10")
        control_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Website selection
        ttk.Label(control_frame, text="Test Website:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.site_var = tk.StringVar(value=self.test_sites[0]["name"])
        self.site_combo = ttk.Combobox(control_frame, textvariable=self.site_var, 
                                      values=[site["name"] for site in self.test_sites], width=20)
        self.site_combo.grid(row=0, column=1, padx=(0, 20))
        self.site_combo.bind("<<ComboboxSelected>>", self.on_site_change)
        
        # Custom URL entry
        ttk.Label(control_frame, text="Custom URL:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        self.custom_url_var = tk.StringVar()
        self.custom_url_entry = ttk.Entry(control_frame, textvariable=self.custom_url_var, width=40)
        self.custom_url_entry.grid(row=0, column=3, padx=(0, 20))
        
        # Test parameters
        ttk.Label(control_frame, text="Test Count:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.test_count_var = tk.StringVar(value="10")
        ttk.Spinbox(control_frame, from_=1, to=100, textvariable=self.test_count_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=(10, 0))
        
        ttk.Label(control_frame, text="Interval (sec):").grid(row=1, column=2, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.interval_var = tk.StringVar(value="5")
        ttk.Spinbox(control_frame, from_=1, to=60, textvariable=self.interval_var, width=10).grid(row=1, column=3, sticky=tk.W, pady=(10, 0))
        
        # Action buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=(10, 0))
        
        self.start_btn = ttk.Button(button_frame, text="Start Analysis", command=self.start_analysis)
        self.start_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_btn = ttk.Button(button_frame, text="Stop", command=self.stop_analysis, state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=1, padx=(0, 10))
        
        ttk.Button(button_frame, text="Clear Data", command=self.clear_data).grid(row=0, column=2, padx=(0, 10))
        ttk.Button(button_frame, text="Export Data", command=self.export_data).grid(row=0, column=3, padx=(0, 10))
        ttk.Button(button_frame, text="Refresh Clients", command=self.refresh_clients).grid(row=0, column=4, padx=(0, 10))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(control_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(control_frame, textvariable=self.status_var)
        self.status_label.grid(row=4, column=0, columnspan=4, pady=(5, 0))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Local Data Tab
        local_frame = ttk.Frame(self.notebook)
        self.notebook.add(local_frame, text="Local Data")
        self.setup_local_tab(local_frame)
        
        # Multi-Client Tab
        multi_frame = ttk.Frame(self.notebook)
        self.notebook.add(multi_frame, text="Multi-Client View")
        self.setup_multi_client_tab(multi_frame)
        
        # Log Tab
        log_frame = ttk.Frame(self.notebook)
        self.notebook.add(log_frame, text="Activity Log")
        self.setup_log_tab(log_frame)
        
    def setup_local_tab(self, parent):
        parent.columnconfigure(1, weight=1)
        parent.rowconfigure(0, weight=1)
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(parent, text="Local Statistics", padding="10")
        stats_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        self.local_stats_text = tk.Text(stats_frame, height=15, width=35, font=("Courier", 10))
        self.local_stats_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Local plots
        plot_frame = ttk.LabelFrame(parent, text="Local Performance", padding="10")
        plot_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        plot_frame.columnconfigure(0, weight=1)
        plot_frame.rowconfigure(0, weight=1)
        
        self.local_fig, (self.local_ax1, self.local_ax2) = plt.subplots(2, 1, figsize=(8, 8))
        self.local_fig.tight_layout(pad=3.0)
        
        self.local_canvas = FigureCanvasTkAgg(self.local_fig, master=plot_frame)
        self.local_canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.setup_local_plots()
        
    def setup_multi_client_tab(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        
        # Connected clients frame
        clients_frame = ttk.LabelFrame(parent, text="Connected Clients", padding="10")
        clients_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        clients_frame.columnconfigure(0, weight=1)
        
        # Create treeview for clients
        columns = ('Name', 'Status', 'Tests', 'Avg Speed', 'Last Seen')
        self.clients_tree = ttk.Treeview(clients_frame, columns=columns, show='headings', height=6)
        
        for col in columns:
            self.clients_tree.heading(col, text=col)
            self.clients_tree.column(col, width=120)
        
        self.clients_tree.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Multi-client plots with enhanced comparison
        multi_plot_frame = ttk.LabelFrame(parent, text="Multi-Client Speed Comparison", padding="10")
        multi_plot_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        multi_plot_frame.columnconfigure(0, weight=1)
        multi_plot_frame.rowconfigure(0, weight=1)
        
        self.multi_fig, ((self.multi_ax1, self.multi_ax2), (self.multi_ax3, self.multi_ax4)) = plt.subplots(2, 2, figsize=(12, 10))
        self.multi_fig.tight_layout(pad=3.0)
        
        self.multi_canvas = FigureCanvasTkAgg(self.multi_fig, master=multi_plot_frame)
        self.multi_canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.setup_multi_plots()
        
    def setup_log_tab(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        
        # Log frame
        log_frame = ttk.Frame(parent)
        log_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, font=("Courier", 9))
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
    def setup_local_plots(self):
        self.local_ax1.set_title("Local Speed Over Time")
        self.local_ax1.set_xlabel("Time")
        self.local_ax1.set_ylabel("Speed (Mbps)")
        self.local_ax1.grid(True, alpha=0.3)
        
        self.local_ax2.set_title("Local Speed Distribution")
        self.local_ax2.set_xlabel("Speed (Mbps)")
        self.local_ax2.set_ylabel("Frequency")
        self.local_ax2.grid(True, alpha=0.3)
        
        self.local_canvas.draw()
        
    def setup_multi_plots(self):
        # Plot 1: Speed over time comparison
        self.multi_ax1.set_title("Speed Over Time - All Clients")
        self.multi_ax1.set_xlabel("Time")
        self.multi_ax1.set_ylabel("Speed (Mbps)")
        self.multi_ax1.grid(True, alpha=0.3)
        
        # Plot 2: Average speed comparison
        self.multi_ax2.set_title("Average Speed by Client")
        self.multi_ax2.set_xlabel("Client")
        self.multi_ax2.set_ylabel("Average Speed (Mbps)")
        self.multi_ax2.grid(True, alpha=0.3)
        
        # Plot 3: Speed distribution comparison
        self.multi_ax3.set_title("Speed Distribution Comparison")
        self.multi_ax3.set_xlabel("Speed (Mbps)")
        self.multi_ax3.set_ylabel("Frequency")
        self.multi_ax3.grid(True, alpha=0.3)
        
        # Plot 4: Performance over time (heatmap style)
        self.multi_ax4.set_title("Client Performance Timeline")
        self.multi_ax4.set_xlabel("Time")
        self.multi_ax4.set_ylabel("Client")
        self.multi_ax4.grid(True, alpha=0.3)
        
        self.multi_canvas.draw()
        
    def on_site_change(self, event=None):
        selected = self.site_var.get()
        for site in self.test_sites:
            if site["name"] == selected:
                self.custom_url_var.set(site["url"])
                break
                
    def log_message(self, message, tab="local"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def register_with_server(self):
        def register():
            try:
                self.server_url = self.server_url_var.get()
                payload = {
                    'client_id': self.client_id,
                    'client_name': self.client_name_var.get()
                }
                
                response = requests.post(f"{self.server_url}/api/register", 
                                       json=payload, timeout=5)
                
                if response.status_code == 200:
                    self.is_connected = True
                    self.conn_status_var.set("Connected")
                    self.conn_status_label.configure(foreground="green")
                    self.log_message(f"Registered with server as {self.client_name}")
                else:
                    self.is_connected = False
                    self.conn_status_var.set("Connection Failed")
                    self.conn_status_label.configure(foreground="red")
                    self.log_message(f"Failed to register: {response.text}")
                    
            except Exception as e:
                self.is_connected = False
                self.conn_status_var.set("Offline")
                self.conn_status_label.configure(foreground="red")
                self.log_message(f"Server connection error: {str(e)}")
                
        threading.Thread(target=register, daemon=True).start()
        
    def start_sync_thread(self):
        def sync_data():
            while True:
                try:
                    if self.is_connected:
                        # Fetch dashboard data
                        response = requests.get(f"{self.server_url}/api/dashboard", timeout=5)
                        if response.status_code == 200:
                            data = response.json()
                            self.root.after(0, self.update_multi_client_view, data)
                            
                except Exception as e:
                    self.log_message(f"Sync error: {str(e)}")
                    
                time.sleep(2)  # Sync every 2 seconds
                
        threading.Thread(target=sync_data, daemon=True).start()
        
    def update_multi_client_view(self, data):
        # Update clients tree
        for item in self.clients_tree.get_children():
            self.clients_tree.delete(item)
            
        for client in data.get('clients', []):
            status = "Online" if client['active'] else "Offline"
            self.clients_tree.insert('', 'end', values=(
                client['name'],
                status,
                client['test_count'],
                f"{client['avg_speed']:.2f} Mbps",
                client['last_seen']
            ))
            
        # Update multi-client plots
        self.update_multi_plots(data)
        
    def update_multi_plots(self, data):
        # Clear all plots
        self.multi_ax1.clear()
        self.multi_ax2.clear()
        self.multi_ax3.clear()
        self.multi_ax4.clear()
        
        clients = data.get('clients', [])
        if not clients:
            self.setup_multi_plots()
            return
            
        # Filter clients with data
        active_clients = [c for c in clients if c['data'] and c['avg_speed'] > 0]
        if not active_clients:
            self.setup_multi_plots()
            return
            
        colors = plt.cm.Set3(range(len(active_clients)))
        
        # Plot 1: Speed over time for all clients
        for i, client in enumerate(active_clients):
            if client['data']:
                times = [d['time'] for d in client['data']]
                speeds = [d['speed'] for d in client['data']]
                self.multi_ax1.plot(times, speeds, marker='o', label=client['name'], 
                                   color=colors[i], alpha=0.7, linewidth=2)
                
        self.multi_ax1.set_title("Speed Over Time - All Clients")
        self.multi_ax1.set_xlabel("Time")
        self.multi_ax1.set_ylabel("Speed (Mbps)")
        self.multi_ax1.legend(loc='best')
        self.multi_ax1.grid(True, alpha=0.3)
        plt.setp(self.multi_ax1.xaxis.get_majorticklabels(), rotation=45)
        
        # Plot 2: Average speed comparison (bar chart)
        client_names = [c['name'][:15] for c in active_clients]  # Truncate long names
        avg_speeds = [c['avg_speed'] for c in active_clients]
        
        bars = self.multi_ax2.bar(client_names, avg_speeds, color=colors, alpha=0.8)
        self.multi_ax2.set_title("Average Speed by Client")
        self.multi_ax2.set_xlabel("Client")
        self.multi_ax2.set_ylabel("Average Speed (Mbps)")
        self.multi_ax2.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar, speed in zip(bars, avg_speeds):
            height = bar.get_height()
            self.multi_ax2.text(bar.get_x() + bar.get_width()/2., height,
                              f'{speed:.1f}', ha='center', va='bottom', fontweight='bold')
        
        plt.setp(self.multi_ax2.xaxis.get_majorticklabels(), rotation=45)
        
        # Plot 3: Speed distribution comparison (histogram)
        all_client_speeds = []
        client_labels = []
        
        for i, client in enumerate(active_clients):
            speeds = [d['speed'] for d in client['data']]
            if speeds:
                self.multi_ax3.hist(speeds, bins=15, alpha=0.6, label=client['name'], 
                                   color=colors[i], edgecolor='black')
        
        self.multi_ax3.set_title("Speed Distribution Comparison")
        self.multi_ax3.set_xlabel("Speed (Mbps)")
        self.multi_ax3.set_ylabel("Frequency")
        self.multi_ax3.legend(loc='best')
        self.multi_ax3.grid(True, alpha=0.3)
        
        # Plot 4: Performance timeline (scatter plot)
        for i, client in enumerate(active_clients):
            if client['data']:
                times = list(range(len(client['data'])))  # Use index as time proxy
                speeds = [d['speed'] for d in client['data']]
                self.multi_ax4.scatter(times, speeds, label=client['name'], 
                                      color=colors[i], alpha=0.7, s=50)
        
        self.multi_ax4.set_title("Client Performance Timeline")
        self.multi_ax4.set_xlabel("Test Sequence")
        self.multi_ax4.set_ylabel("Speed (Mbps)")
        self.multi_ax4.legend(loc='best')
        self.multi_ax4.grid(True, alpha=0.3)
        
        self.multi_fig.tight_layout(pad=3.0)
        self.multi_canvas.draw()
        
    def update_local_stats(self):
        if not self.local_data:
            self.local_stats_text.delete(1.0, tk.END)
            self.local_stats_text.insert(tk.END, "No local data available")
            return
            
        speeds = [entry["speed"] for entry in self.local_data]
        stats = {
            "Tests Run": len(speeds),
            "Average Speed": f"{sum(speeds)/len(speeds):.2f} Mbps",
            "Max Speed": f"{max(speeds):.2f} Mbps",
            "Min Speed": f"{min(speeds):.2f} Mbps",
            "Median": f"{sorted(speeds)[len(speeds)//2]:.2f} Mbps"
        }
        
        self.local_stats_text.delete(1.0, tk.END)
        for key, value in stats.items():
            self.local_stats_text.insert(tk.END, f"{key:12}: {value}\n")
            
    def update_local_plots(self):
        if not self.local_data:
            return
            
        # Clear previous plots
        self.local_ax1.clear()
        self.local_ax2.clear()
        
        # Extract data
        timestamps = [entry["timestamp"] for entry in self.local_data]
        speeds = [entry["speed"] for entry in self.local_data]
        
        # Plot 1: Speed over time
        self.local_ax1.plot(timestamps, speeds, marker='o', color='blue', alpha=0.7)
        self.local_ax1.set_title("Local Speed Over Time")
        self.local_ax1.set_xlabel("Time")
        self.local_ax1.set_ylabel("Speed (Mbps)")
        self.local_ax1.grid(True, alpha=0.3)
        plt.setp(self.local_ax1.xaxis.get_majorticklabels(), rotation=45)
        
        # Plot 2: Distribution
        self.local_ax2.hist(speeds, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
        self.local_ax2.set_title("Local Speed Distribution")
        self.local_ax2.set_xlabel("Speed (Mbps)")
        self.local_ax2.set_ylabel("Frequency")
        self.local_ax2.grid(True, alpha=0.3)
        
        self.local_fig.tight_layout(pad=3.0)
        self.local_canvas.draw()
        
    def download_and_measure(self, url):
        try:
            start_time = time.time()
            
            if "speed.cloudflare.com" in url:
                response = requests.get(url, stream=True, timeout=30, verify=certifi.where())
                size = 0
                for chunk in response.iter_content(chunk_size=1024*1024):
                    if chunk:
                        size += len(chunk)
            else:
                response = requests.get(url, timeout=30, verify=certifi.where())
                size = len(response.content)
                
            duration = time.time() - start_time
            
            if duration > 0:
                speed_mbps = round((size * 8) / (1024 * 1024 * duration), 2)
                return speed_mbps
            else:
                return 0
                
        except Exception as e:
            self.log_message(f"Download error: {str(e)}")
            return 0
            
    def send_to_server(self, speed, site):
        if not self.is_connected:
            return False
            
        try:
            payload = {
                'client_id': self.client_id,
                'speed': speed,
                'timestamp': datetime.now().strftime("%H:%M:%S"),
                'site': site
            }
            
            response = requests.post(f"{self.server_url}/api/report", 
                                   json=payload, timeout=5)
            return response.status_code == 200
            
        except Exception as e:
            self.log_message(f"Server send error: {str(e)}")
            return False
            
    def analysis_worker(self):
        try:
            test_count = int(self.test_count_var.get())
            interval = int(self.interval_var.get())
            url = self.custom_url_var.get()
            site_name = self.site_var.get()
            
            if not url:
                self.log_message("Please enter a valid URL")
                return
                
            self.log_message(f"Starting local analysis: {test_count} tests from {site_name}")
            
            for i in range(test_count):
                if not self.is_running:
                    break
                    
                self.status_var.set(f"Running test {i+1}/{test_count}")
                self.progress_var.set((i + 1) / test_count * 100)
                
                speed = self.download_and_measure(url)
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                # Store local data
                data_point = {
                    "timestamp": timestamp,
                    "speed": speed,
                    "site": site_name,
                    "url": url
                }
                self.local_data.append(data_point)
                
                # Send to server
                server_success = self.send_to_server(speed, site_name)
                server_status = "Server: OK" if server_success else "Server: Failed"
                
                self.log_message(f"Test {i+1}: {speed} Mbps ({server_status})")
                
                # Update UI
                self.root.after(0, self.update_local_stats)
                self.root.after(0, self.update_local_plots)
                
                if i < test_count - 1 and self.is_running:
                    time.sleep(interval)
                    
            self.status_var.set("Analysis complete")
            self.log_message("Local analysis completed")
            
        except Exception as e:
            self.log_message(f"Analysis error: {str(e)}")
            self.status_var.set("Analysis failed")
        finally:
            self.is_running = False
            self.root.after(0, lambda: self.start_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.stop_btn.config(state=tk.DISABLED))
            
    def start_analysis(self):
        if self.is_running:
            return
            
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress_var.set(0)
        
        # Start analysis in separate thread
        thread = threading.Thread(target=self.analysis_worker, daemon=True)
        thread.start()
        
    def stop_analysis(self):
        self.is_running = False
        self.status_var.set("Analysis stopped")
        self.log_message("Analysis stopped by user")
        
    def clear_data(self):
        self.local_data = []
        self.update_local_stats()
        self.setup_local_plots()
        self.log_message("Local data cleared")
        self.status_var.set("Ready")
        self.progress_var.set(0)
        
    def export_data(self):
        if not self.local_data:
            messagebox.showwarning("No Data", "No local data to export")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                if filename.endswith(".json"):
                    with open(filename, 'w') as f:
                        json.dump(self.local_data, f, indent=2)
                else:
                    df = pd.DataFrame(self.local_data)
                    df.to_csv(filename, index=False)
                    
                self.log_message(f"Local data exported to {filename}")
                messagebox.showinfo("Success", f"Data exported successfully")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")
                
    def refresh_clients(self):
        """Force refresh of client data from server"""
        if self.is_connected:
            try:
                response = requests.get(f"{self.server_url}/api/clients", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    self.update_multi_client_view(data)
                    self.log_message("Client data refreshed")
            except Exception as e:
                self.log_message(f"Refresh error: {str(e)}")
        else:
            self.log_message("Not connected to server")

if __name__ == "__main__":
    root = tk.Tk()
    app = MultiClientDownloadAnalyzer(root)
    root.mainloop()
