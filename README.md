# Socket-Programming
Automated Download Analyzer
NAMES:

SANJANA M KULARNI - PES1UG24AM249
SANVIKA M NAIK - PES1UG24AM253
SURYA T -PES1UG24AM300
A comprehensive GUI application for analyzing download speeds from various websites with real-time plotting and data analysis capabilities.

Features
Multi-Website Testing: Test download speeds from Cloudflare, Fast.com, Speedtest.net, Google Drive, or custom URLs
Real-time Analysis: Live speed testing with configurable intervals and test counts
Data Visualization: Interactive plots showing speed trends and distributions
Statistics Panel: Real-time statistics including average, max, min, and median speeds
Activity Logging: Detailed timestamped logs of all testing activities
Data Export: Export results to CSV or JSON formats
Modern UI: Clean, intuitive interface with progress tracking
Installation
Install the required dependencies:
pip install -r requirements.txt
Run the application:
python download_analyzer.py
Usage
Basic Usage
Select a test website from the dropdown or enter a custom URL
Configure the number of tests and interval between tests
Click "Start Analysis" to begin testing
View real-time results in the statistics panel and plots
Export data using the "Export Data" button
Advanced Features
Custom URLs: Test any downloadable content by entering a custom URL
Batch Testing: Run multiple tests automatically with configurable intervals
Data Analysis: View speed trends over time and distribution histograms
Export Options: Save results as CSV for spreadsheet analysis or JSON for programmatic use
Test Websites Included
Cloudflare: Uses Cloudflare's speed test endpoint (10MB download)
Fast.com: Netflix's speed test service
Speedtest.net: Popular speed testing platform
Google Drive: Test download speeds from cloud storage
Custom: Test any URL you specify
Technical Details
Architecture
GUI Framework: Tkinter with ttk widgets for modern appearance
Data Processing: Pandas for data manipulation and analysis
Visualization: Matplotlib with interactive plotting
Web Requests: Requests library with SSL verification
HTML Parsing: BeautifulSoup for web scraping capabilities
Performance Metrics
Download speed measured in Mbps (megabits per second)
Timestamp tracking for each measurement
Statistical analysis including mean, median, min, max
Real-time plot updates during testing
Data Storage
In-memory storage during runtime
CSV export for spreadsheet compatibility
JSON export for programmatic access
Configurable test parameters
Troubleshooting
Common Issues
Connection Errors: Check internet connection and URL validity
Slow Performance: Reduce test count or increase interval time
SSL Errors: Ensure certifi is properly installed
UI Freezing: The application uses threading to prevent UI freezing
Error Handling
Network timeouts are handled gracefully
Invalid URLs show appropriate error messages
Export failures provide detailed error information
Test interruptions can be resumed
Requirements
Python 3.7 or higher
Windows, macOS, or Linux
Internet connection for testing
2GB RAM minimum (for large datasets)
License
This project is open source and available under the MIT License.
