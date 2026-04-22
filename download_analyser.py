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
from urllib.parse import urljoin, urlparse
import certifi
from bs4 import BeautifulSoup
import re

class DownloadAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Automated Download Analyzer")
        self.root.geometry("1200x800")
        
        # Data storage
        self.download_data = []
        self.is_running = False
        
        # Test websites
        self.test_sites = [
            {"name": "Cloudflare", "url": "https://speed.cloudflare.com/__down?bytes=10485760"},
            {"name": "Fast.com", "url": "https://fast.com"},
            {"name": "Speedtest.net", "url": "https://www.speedtest.net"},
            {"name": "Google Drive", "url": "https://drive.google.com"},
            {"name": "Custom", "url": ""}
        ]
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Control Panel
        control_frame = ttk.LabelFrame(main_frame, text="Control Panel", padding="10")
        control_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
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
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(control_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(control_frame, textvariable=self.status_var)
        self.status_label.grid(row=4, column=0, columnspan=4, pady=(5, 0))
        
        # Left panel - Log and Stats
        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_frame.rowconfigure(1, weight=1)
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(left_frame, text="Statistics", padding="10")
        stats_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.stats_text = tk.Text(stats_frame, height=8, width=40, font=("Courier", 10))
        self.stats_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Log frame
        log_frame = ttk.LabelFrame(left_frame, text="Activity Log", padding="10")
        log_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=20, width=40, font=("Courier", 9))
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Right panel - Plots
        right_frame = ttk.LabelFrame(main_frame, text="Data Visualization", padding="10")
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.rowconfigure(0, weight=1)
        right_frame.columnconfigure(0, weight=1)
        
        # Create matplotlib figure
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(8, 8))
        self.fig.tight_layout(pad=3.0)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Initialize plots
        self.setup_plots()
        
    def setup_plots(self):
        # Speed over time plot
        self.ax1.set_title("Download Speed Over Time")
        self.ax1.set_xlabel("Time")
        self.ax1.set_ylabel("Speed (Mbps)")
        self.ax1.grid(True, alpha=0.3)
        
        # Distribution plot
        self.ax2.set_title("Speed Distribution")
        self.ax2.set_xlabel("Speed (Mbps)")
        self.ax2.set_ylabel("Frequency")
        self.ax2.grid(True, alpha=0.3)
        
        self.canvas.draw()
        
    def on_site_change(self, event=None):
        selected = self.site_var.get()
        for site in self.test_sites:
            if site["name"] == selected:
                self.custom_url_var.set(site["url"])
                break
                
    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def update_stats(self):
        if not self.download_data:
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(tk.END, "No data available")
            return
            
        speeds = [entry["speed"] for entry in self.download_data]
        stats = {
            "Tests Run": len(speeds),
            "Average Speed": f"{sum(speeds)/len(speeds):.2f} Mbps",
            "Max Speed": f"{max(speeds):.2f} Mbps",
            "Min Speed": f"{min(speeds):.2f} Mbps",
            "Median": f"{sorted(speeds)[len(speeds)//2]:.2f} Mbps"
        }
        
        self.stats_text.delete(1.0, tk.END)
        for key, value in stats.items():
            self.stats_text.insert(tk.END, f"{key:12}: {value}\n")
            
    def update_plots(self):
        if not self.download_data:
            return
            
        # Clear previous plots
        self.ax1.clear()
        self.ax2.clear()
        
        # Extract data
        timestamps = [entry["timestamp"] for entry in self.download_data]
        speeds = [entry["speed"] for entry in self.download_data]
        sites = [entry["site"] for entry in self.download_data]
        
        # Plot 1: Speed over time
        unique_sites = list(set(sites))
        colors = plt.cm.Set3(range(len(unique_sites)))
        
        for i, site in enumerate(unique_sites):
            site_data = [(t, s) for t, s, si in zip(timestamps, speeds, sites) if si == site]
            if site_data:
                site_times, site_speeds = zip(*site_data)
                self.ax1.plot(site_times, site_speeds, marker='o', label=site, color=colors[i], alpha=0.7)
                
        self.ax1.set_title("Download Speed Over Time")
        self.ax1.set_xlabel("Time")
        self.ax1.set_ylabel("Speed (Mbps)")
        self.ax1.legend()
        self.ax1.grid(True, alpha=0.3)
        plt.setp(self.ax1.xaxis.get_majorticklabels(), rotation=45)
        
        # Plot 2: Distribution
        self.ax2.hist(speeds, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
        self.ax2.set_title("Speed Distribution")
        self.ax2.set_xlabel("Speed (Mbps)")
        self.ax2.set_ylabel("Frequency")
        self.ax2.grid(True, alpha=0.3)
        
        self.fig.tight_layout(pad=3.0)
        self.canvas.draw()
        
    def download_and_measure(self, url):
        try:
            start_time = time.time()
            
            # Handle different types of download URLs
            if "speed.cloudflare.com" in url:
                # Cloudflare speed test
                response = requests.get(url, stream=True, timeout=30, verify=certifi.where())
                size = 0
                for chunk in response.iter_content(chunk_size=1024*1024):
                    if chunk:
                        size += len(chunk)
            else:
                # Generic download - try to find a downloadable file
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
            
    def analysis_worker(self):
        try:
            test_count = int(self.test_count_var.get())
            interval = int(self.interval_var.get())
            url = self.custom_url_var.get()
            site_name = self.site_var.get()
            
            if not url:
                self.log_message("Please enter a valid URL")
                return
                
            self.log_message(f"Starting analysis: {test_count} tests from {site_name}")
            
            for i in range(test_count):
                if not self.is_running:
                    break
                    
                self.status_var.set(f"Running test {i+1}/{test_count}")
                self.progress_var.set((i + 1) / test_count * 100)
                
                speed = self.download_and_measure(url)
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                # Store data
                data_point = {
                    "timestamp": timestamp,
                    "speed": speed,
                    "site": site_name,
                    "url": url
                }
                self.download_data.append(data_point)
                
                self.log_message(f"Test {i+1}: {speed} Mbps")
                
                # Update UI in main thread
                self.root.after(0, self.update_stats)
                self.root.after(0, self.update_plots)
                
                if i < test_count - 1 and self.is_running:
                    time.sleep(interval)
                    
            self.status_var.set("Analysis complete")
            self.log_message("Analysis completed successfully")
            
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
        self.download_data = []
        self.update_stats()
        self.setup_plots()
        self.log_message("Data cleared")
        self.status_var.set("Ready")
        self.progress_var.set(0)
        
    def export_data(self):
        if not self.download_data:
            messagebox.showwarning("No Data", "No data to export")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                if filename.endswith(".json"):
                    with open(filename, 'w') as f:
                        json.dump(self.download_data, f, indent=2)
                else:
                    df = pd.DataFrame(self.download_data)
                    df.to_csv(filename, index=False)
                    
                self.log_message(f"Data exported to {filename}")
                messagebox.showinfo("Success", f"Data exported successfully")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DownloadAnalyzer(root)
    root.mainloop()
