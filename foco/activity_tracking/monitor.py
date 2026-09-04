"""
Activity Monitor - Real-time activity detection
Tracks active windows, applications, and detects idle time
"""
import psutil
import ctypes
from datetime import datetime, timedelta
from .classifier import CategoryEngine

try:
    import win32gui
    import win32process
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False

class ActivityMonitor:
    def __init__(self, data_logger, window_provider=None, idle_seconds_provider=None,
                 now_provider=None, config_path="config.json"):
        self.data_logger = data_logger
        self.category_engine = CategoryEngine(config_path)
        self.window_provider = window_provider or self.get_active_window_info
        self.idle_seconds_provider = idle_seconds_provider or self.get_idle_seconds
        self.now_provider = now_provider or datetime.now
        self.current_app = None
        self.current_window_title = ""
        idle_minutes = self.category_engine.config.get('idle_timeout', 5)
        self.idle_threshold = max(1, float(idle_minutes)) * 60
        self.session_start = None
        self._idle = False
        
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
    
    def get_idle_seconds(self):
        """Return seconds since the last keyboard or mouse input on Windows."""
        if not WINDOWS_AVAILABLE:
            return 0

        class LASTINPUTINFO(ctypes.Structure):
            _fields_ = [('cbSize', ctypes.c_uint), ('dwTime', ctypes.c_uint)]

        try:
            info = LASTINPUTINFO()
            info.cbSize = ctypes.sizeof(info)
            if not ctypes.windll.user32.GetLastInputInfo(ctypes.byref(info)):
                return 0
            elapsed_ms = ctypes.windll.kernel32.GetTickCount64() - info.dwTime
            return max(0, elapsed_ms / 1000)
        except (AttributeError, OSError):
            return 0
    
    def update(self):
        """Main update loop - called every second"""
        current_time = self.now_provider()
        if self.session_start and current_time.date() != self.session_start.date():
            midnight = datetime.combine(current_time.date(), datetime.min.time())
            self.end_current_session(end_at=midnight)
            self.current_app = None
            self.current_window_title = ""

        idle_seconds = self.idle_seconds_provider()
        if idle_seconds >= self.idle_threshold:
            if not self._idle and self.session_start:
                idle_started = current_time - timedelta(seconds=idle_seconds)
                self.end_current_session(end_at=idle_started)
                self.current_app = None
                self.current_window_title = ""
            self._idle = True
            return

        self._idle = False
            
        # Get current application info
        app_name, window_title = self.window_provider()
        
        # A title change can represent a browser tab, document, or project change.
        if app_name != self.current_app or window_title != self.current_window_title:
            if self.current_app and self.session_start:
                # Log the previous session
                self.end_current_session()
            
            # Start new session
            self.start_new_session(
                app_name, window_title,
                meaningful_context_switch=bool(self.current_app and app_name != self.current_app),
            )
        
        self.current_app = app_name
        self.current_window_title = window_title
    
    def start_new_session(self, app_name, window_title, meaningful_context_switch=False):
        """Start tracking a new application session"""
        self.session_start = self.now_provider()
        category, reason = self.category_engine.classify_activity(app_name, window_title)
        
        # Log session start
        session_data = {
            'start_time': self.session_start.strftime('%H:%M:%S'),
            'application': app_name,
            'window_title': window_title,
            'category': category,
            'classification_reason': reason,
            'meaningful_context_switch': meaningful_context_switch,
            'is_pseudo_productive': self.category_engine.is_pseudo_productive(app_name, window_title)
        }
        
        self.data_logger.start_session(session_data)
    
    def end_current_session(self, end_at=None):
        """End the current application session"""
        if self.session_start:
            end_at = max(self.session_start, end_at or self.now_provider())
            duration = (end_at - self.session_start).total_seconds() / 60
            
            if duration > 0:
                session_data = {
                    'end_time': end_at.strftime('%H:%M:%S'),
                    'duration_minutes': round(duration, 1),
                    'application': self.current_app,
                    'window_title': self.current_window_title
                }
                
                self.data_logger.end_session(session_data)
            elif hasattr(self.data_logger, 'cancel_current_session'):
                self.data_logger.cancel_current_session()
            self.session_start = None

    def stop(self):
        """Flush the active segment during application shutdown."""
        if self.session_start:
            self.end_current_session()
    
    def get_current_activity(self):
        """Get current activity information for dashboard"""
        if self.session_start and self.current_app:
            duration = (self.now_provider() - self.session_start).total_seconds() / 60
            category, reason = self.category_engine.classify_activity(
                self.current_app, self.current_window_title
            )
            
            return {
                'application': self.current_app,
                'category': category,
                'classification_reason': reason,
                'duration': round(duration, 1),
                'is_pseudo_productive': self.category_engine.is_pseudo_productive(self.current_app, self.current_window_title)
            }
        
        return None
