"""
Data Logger - Local data storage and retrieval
Handles saving/loading productivity data and historical summaries
"""
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict

class DataLogger:
    def __init__(self):
        self.data_dir = "productivity_data"
        self.ensure_data_dir()
        self.current_session = None
        self.today_data = self.load_today_data()
    
    def ensure_data_dir(self):
        """Create data directory if it doesn't exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def get_today_filename(self):
        """Get filename for today's data"""
        today = datetime.now().strftime('%Y-%m-%d')
        return os.path.join(self.data_dir, f"{today}.json")
    
    def load_today_data(self):
        """Load today's productivity data"""
        filename = self.get_today_filename()
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        # Return empty structure for new day
        return {
            "date": datetime.now().strftime('%Y-%m-%d'),
            "sessions": [],
            "daily_summary": {
                "building": 0,
                "studying": 0,
                "applying": 0,
                "knowledge": 0,
                "pseudo_productive": 0,
                "context_switches": 0,
                "total_productive": 0
            }
        }
    
    def save_today_data(self):
        """Save today's data to file"""
        filename = self.get_today_filename()
        try:
            with open(filename, 'w') as f:
                json.dump(self.today_data, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def start_session(self, session_data):
        """Start a new tracking session"""
        self.current_session = session_data.copy()
        self.today_data["daily_summary"]["context_switches"] += 1
    
    def end_session(self, session_data):
        """End current session and log the data"""
        if not self.current_session:
            return
        
        # Merge session data
        complete_session = self.current_session.copy()
        complete_session.update(session_data)
        
        # Add to sessions list
        self.today_data["sessions"].append(complete_session)
        
        # Update daily summary
        category = complete_session.get('category', 'knowledge').lower()
        duration = complete_session.get('duration_minutes', 0)
        
        if complete_session.get('is_pseudo_productive', False):
            self.today_data["daily_summary"]["pseudo_productive"] += duration
        else:
            self.today_data["daily_summary"][category] += duration
            self.today_data["daily_summary"]["total_productive"] += duration
        
        # Save to file
        self.save_today_data()
        self.current_session = None
    
    def get_today_summary(self):
        """Get today's productivity summary"""
        return self.today_data["daily_summary"].copy()
    
    def get_current_session_info(self):
        """Get information about the current session"""
        return self.current_session.copy() if self.current_session else None
    
    def get_weekly_data(self, start_date=None):
        """Get data for the current week"""
        if start_date is None:
            # Get Monday of current week
            today = datetime.now()
            start_date = today - timedelta(days=today.weekday())
        
        weekly_data = []
        for i in range(7):
            date = start_date + timedelta(days=i)
            filename = os.path.join(self.data_dir, f"{date.strftime('%Y-%m-%d')}.json")
            
            if os.path.exists(filename):
                try:
                    with open(filename, 'r') as f:
                        day_data = json.load(f)
                        weekly_data.append(day_data)
                except:
                    weekly_data.append(self.get_empty_day_data(date))
            else:
                weekly_data.append(self.get_empty_day_data(date))
        
        return weekly_data
    
    def get_monthly_data(self, year=None, month=None):
        """Get data for the current month"""
        if year is None or month is None:
            now = datetime.now()
            year = now.year
            month = now.month
        
        # Get first and last day of month
        first_day = datetime(year, month, 1)
        if month == 12:
            last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = datetime(year, month + 1, 1) - timedelta(days=1)
        
        monthly_data = []
        current_date = first_day
        
        while current_date <= last_day:
            filename = os.path.join(self.data_dir, f"{current_date.strftime('%Y-%m-%d')}.json")
            
            if os.path.exists(filename):
                try:
                    with open(filename, 'r') as f:
                        day_data = json.load(f)
                        monthly_data.append(day_data)
                except:
                    monthly_data.append(self.get_empty_day_data(current_date))
            else:
                monthly_data.append(self.get_empty_day_data(current_date))
            
            current_date += timedelta(days=1)
        
        return monthly_data
    
    def get_empty_day_data(self, date):
        """Get empty data structure for a day"""
        return {
            "date": date.strftime('%Y-%m-%d'),
            "sessions": [],
            "daily_summary": {
                "building": 0,
                "studying": 0,
                "applying": 0,
                "knowledge": 0,
                "pseudo_productive": 0,
                "context_switches": 0,
                "total_productive": 0
            }
        }
    
    def get_available_dates(self):
        """Get list of all available data dates"""
        dates = []
        if os.path.exists(self.data_dir):
            for filename in os.listdir(self.data_dir):
                if filename.endswith('.json') and len(filename) == 15:  # YYYY-MM-DD.json
                    dates.append(filename[:-5])  # Remove .json extension
        return sorted(dates)

    def get_recent_activities(self, limit=50):
        """Return flattened recent session activities for Activities tab.
        Each session entry transformed to a simple dict: start_time, end_time, label, category, duration_minutes."""
        activities = []
        try:
            sessions = self.today_data.get('sessions', [])
            for s in sessions[-limit:]:
                start = s.get('start_time') or s.get('timestamp') or ''
                end = s.get('end_time', '')
                duration = s.get('duration_minutes') or s.get('duration', 0)
                activities.append({
                    'start_time': start,
                    'end_time': end,
                    'label': s.get('activity') or s.get('application') or s.get('window_title') or 'Session',
                    'category': s.get('category', 'unknown'),
                    'duration_minutes': duration
                })
        except Exception:
            pass
        return activities[-limit:]

    def save_activity_overrides(self, rows):
        """Persist manual edits (lightweight override file)."""
        try:
            override_path = os.path.join(self.data_dir, 'activity_overrides.json')
            with open(override_path, 'w', encoding='utf-8') as f:
                json.dump(rows, f, indent=2)
        except Exception as e:
            print(f"Error saving overrides: {e}")