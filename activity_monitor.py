"""
Activity Monitor - Real-time activity detection
Tracks active windows, applications, and detects idle time
"""
import psutil
import time
import json
from datetime import datetime
from category_engine import CategoryEngine

try:
    import win32gui
    import win32process
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False

class ActivityMonitor:
    def __init__(self, data_logger):
        self.data_logger = data_logger
        self.category_engine = CategoryEngine()
        self.current_app = None
        self.current_window_title = ""
        self.last_activity_time = time.time()
        self.idle_threshold = 5 * 60  # 5 minutes in seconds
        self.session_start = None
        
    def get_active_window_info(self):
        """Get information about the currently active window"""
        if not WINDOWS_AVAILABLE:
            return "Unknown", "Unknown"
            
        try:
            # Get active window handle
            hwnd = win32gui.GetForegroundWindow()
            
            # Get window title
            window_title = win32gui.GetWindowText(hwnd)
            
            # Get process ID
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            
            # Get process name
            try:
                process = psutil.Process(pid)
                process_name = process.name()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                process_name = "Unknown"
                
            return process_name, window_title
        except Exception:
            return "Unknown", "Unknown"
    
    def detect_keyboard_activity(self):
        """Simple activity detection - checks if processes are active"""
        # For simplicity, we'll consider the system active if CPU usage > 1%
        # In a full implementation, you'd use keyboard/mouse hooks
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            return cpu_percent > 1.0
        except:
            return True  # Default to active
    
    def is_idle(self):
        """Check if user has been idle for too long"""
        if not self.detect_keyboard_activity():
            if time.time() - self.last_activity_time > self.idle_threshold:
                return True
        else:
            self.last_activity_time = time.time()
        return False
    
    def update(self):
        """Main update loop - called every second"""
        if self.is_idle():
            return  # Skip tracking during idle time
            
        # Get current application info
        app_name, window_title = self.get_active_window_info()
        
        # Check if we switched applications
        if app_name != self.current_app:
            if self.current_app and self.session_start:
                # Log the previous session
                self.end_current_session()
            
            # Start new session
            self.start_new_session(app_name, window_title)
        
        self.current_app = app_name
        self.current_window_title = window_title
    
    def start_new_session(self, app_name, window_title):
        """Start tracking a new application session"""
        self.session_start = datetime.now()
        category = self.category_engine.categorize_activity(app_name, window_title)
        
        # Log session start
        session_data = {
            'start_time': self.session_start.strftime('%H:%M:%S'),
            'application': app_name,
            'window_title': window_title,
            'category': category,
            'is_pseudo_productive': self.category_engine.is_pseudo_productive(app_name, window_title)
        }
        
        self.data_logger.start_session(session_data)
    
    def end_current_session(self):
        """End the current application session"""
        if self.session_start:
            duration = (datetime.now() - self.session_start).total_seconds() / 60  # minutes
            
            if duration > 0.5:  # Only log sessions longer than 30 seconds
                session_data = {
                    'end_time': datetime.now().strftime('%H:%M:%S'),
                    'duration_minutes': round(duration, 1),
                    'application': self.current_app,
                    'window_title': self.current_window_title
                }
                
                self.data_logger.end_session(session_data)
    
    def get_current_activity(self):
        """Get current activity information for dashboard"""
        if self.session_start and self.current_app:
            duration = (datetime.now() - self.session_start).total_seconds() / 60
            category = self.category_engine.categorize_activity(self.current_app, self.current_window_title)
            
            return {
                'application': self.current_app,
                'category': category,
                'duration': round(duration, 1),
                'is_pseudo_productive': self.category_engine.is_pseudo_productive(self.current_app, self.current_window_title)
            }
        
        return None