# 📡 Automated Download Analyzer

> A comprehensive GUI application for analyzing download speeds from various websites with real-time plotting and data analysis capabilities.

---

## 👥 Team Members

| Name | USN |
|------|-----|
| Sanjana M Kulkarni | PES1UG24AM249 |
| Sanvika M Naik | PES1UG24AM253 |
| Surya T | PES1UG24AM300 |

---

## ✨ Features

- **Multi-Website Testing** — Test download speeds from Cloudflare, Fast.com, Speedtest.net, Google Drive, or any custom URL
- **Real-time Analysis** — Live speed testing with configurable intervals and test counts
- **Data Visualization** — Interactive plots showing speed trends and distributions
- **Statistics Panel** — Real-time statistics including average, max, min, and median speeds
- **Activity Logging** — Detailed timestamped logs of all testing activities
- **Data Export** — Export results to CSV or JSON formats
- **Modern UI** — Clean, intuitive interface with progress tracking

---

## 🛠️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/automated-download-analyzer.git
cd automated-download-analyzer
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
python download_analyzer.py
```

---

## 🚀 Usage

### Basic Usage

1. Select a test website from the dropdown or enter a custom URL
2. Configure the number of tests and interval between tests
3. Click **"Start Analysis"** to begin testing
4. View real-time results in the statistics panel and plots
5. Export data using the **"Export Data"** button

### Advanced Features

- **Custom URLs** — Test any downloadable content by entering a custom URL
- **Batch Testing** — Run multiple tests automatically with configurable intervals
- **Data Analysis** — View speed trends over time and distribution histograms
- **Export Options** — Save results as CSV for spreadsheet analysis or JSON for programmatic use

---

## 🌐 Test Websites Included

| Source | Description |
|--------|-------------|
| **Cloudflare** | Uses Cloudflare's speed test endpoint (10MB download) |
| **Fast.com** | Netflix's speed test service |
| **Speedtest.net** | Popular speed testing platform |
| **Google Drive** | Test download speeds from cloud storage |
| **Custom** | Test any URL you specify |

---

## 🔧 Technical Details

### Architecture

| Component | Technology |
|-----------|------------|
| GUI Framework | Tkinter with ttk widgets |
| Data Processing | Pandas |
| Visualization | Matplotlib |
| Web Requests | Requests (with SSL verification) |
| HTML Parsing | BeautifulSoup |

### Performance Metrics

- Download speed measured in **Mbps** (megabits per second)
- Timestamp tracking for each measurement
- Statistical analysis: mean, median, min, max
- Real-time plot updates during testing

### Data Storage

- In-memory storage during runtime
- **CSV** export for spreadsheet compatibility
- **JSON** export for programmatic access
- Configurable test parameters

---

## 📋 Requirements

- Python **3.7** or higher
- Windows, macOS, or Linux
- Active internet connection
- Minimum **2GB RAM** (for large datasets)

---

## ❗ Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Connection Errors | Check your internet connection and URL validity |
| Slow Performance | Reduce test count or increase the interval time |
| SSL Errors | Ensure `certifi` is properly installed |
| UI Freezing | The app uses threading — restart if it persists |

### Error Handling

- Network timeouts are handled gracefully
- Invalid URLs show appropriate error messages
- Export failures provide detailed error information
- Test interruptions can be resumed

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<p align="center">Made with ❤️ by Sanjana, Sanvika & Surya</p>
