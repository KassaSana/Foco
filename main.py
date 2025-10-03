"""
Simple ADHD Productivity Tracker
Main entry point for the application
"""
import tkinter as tk
from dashboard import ProductivityDashboard
from activity_monitor import ActivityMonitor
from data_logger import DataLogger
import threading
import time

class ProductivityTracker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ADHD Productivity Tracker")
        self.root.geometry("800x600")
        
        # Initialize components
        self.data_logger = DataLogger()
        self.activity_monitor = ActivityMonitor(self.data_logger)
        self.dashboard = ProductivityDashboard(self.root, self.data_logger, self.activity_monitor)
        
        # Start monitoring in background thread
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.start_monitoring, daemon=True)
        self.monitor_thread.start()
    
    def start_monitoring(self):
        """Run activity monitoring in background"""
        while self.monitoring:
            self.activity_monitor.update()
            time.sleep(1)  # Update every second
    
    def run(self):
        """Start the GUI application"""
        try:
            self.root.mainloop()
        finally:
            self.monitoring = False

if __name__ == "__main__":
    app = ProductivityTracker()
    app.run()