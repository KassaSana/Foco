"""Thread-safe local persistence for activity and focus history."""

import json
import os
import threading
from datetime import datetime, timedelta
from pathlib import Path


SUMMARY_DEFAULTS = {
    "building": 0,
    "studying": 0,
    "applying": 0,
    "knowledge": 0,
    "pseudo_productive": 0,
    "context_switches": 0,
    "total_productive": 0,
    "focus_minutes": 0,
    "focus_sessions": 0,
    "focus_sessions_completed": 0,
}


class DataLogger:
    def __init__(self, data_dir="productivity_data", now_provider=None):
        self.data_dir = str(data_dir)
        self.now_provider = now_provider or datetime.now
        self._lock = threading.RLock()
        self.ensure_data_dir()
        self.current_session = None
        self.current_date = self.now_provider().strftime('%Y-%m-%d')
        self.today_data = self.load_today_data()

    def ensure_data_dir(self):
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)

    def get_today_filename(self):
        return os.path.join(self.data_dir, f"{self.current_date}.json")

    def get_empty_day_data(self, date):
        date_string = date if isinstance(date, str) else date.strftime('%Y-%m-%d')
        return {
            "date": date_string,
            "sessions": [],
            "focus_sessions": [],
            "daily_summary": SUMMARY_DEFAULTS.copy(),
        }

    def _normalize_day_data(self, data, date_string):
        normalized = self.get_empty_day_data(date_string)
        if isinstance(data, dict):
            normalized.update(data)
            normalized["date"] = date_string
            normalized["sessions"] = list(data.get("sessions", []))
            normalized["focus_sessions"] = list(data.get("focus_sessions", []))
            summary = SUMMARY_DEFAULTS.copy()
            summary.update(data.get("daily_summary", {}))
            normalized["daily_summary"] = summary
        return normalized

    def _load_date(self, date_string):
        filename = os.path.join(self.data_dir, f"{date_string}.json")
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    return self._normalize_day_data(json.load(file), date_string)
            except (json.JSONDecodeError, OSError):
                pass
        return self.get_empty_day_data(date_string)

    def load_today_data(self):
        return self._load_date(self.current_date)

    def _rollover_if_needed(self):
        date_string = self.now_provider().strftime('%Y-%m-%d')
        if date_string != self.current_date:
            self.save_today_data()
            self.current_date = date_string
            self.today_data = self._load_date(date_string)
            self.current_session = None

    def save_today_data(self):
        with self._lock:
            filename = Path(self.get_today_filename())
            temp_file = filename.with_suffix('.tmp')
            try:
                with open(temp_file, 'w', encoding='utf-8') as file:
                    json.dump(self.today_data, file, indent=2)
                temp_file.replace(filename)
            except OSError as e:
                print(f"Error saving data: {e}")

    def start_session(self, session_data):
        with self._lock:
            self._rollover_if_needed()
            self.current_session = session_data.copy()
            self.today_data["daily_summary"]["context_switches"] += 1

    def cancel_current_session(self):
        with self._lock:
            summary = self.today_data["daily_summary"]
            summary["context_switches"] = max(0, summary["context_switches"] - 1)
            self.current_session = None

    def end_session(self, session_data):
        with self._lock:
            if not self.current_session:
                return
            complete_session = self.current_session.copy()
            complete_session.update(session_data)
            self.today_data["sessions"].append(complete_session)
            self.current_session = None
            self._recalculate_activity_summary()
            self.save_today_data()

    def _recalculate_activity_summary(self):
        summary = self.today_data["daily_summary"]
        focus_values = {key: summary.get(key, 0) for key in (
            "focus_minutes", "focus_sessions", "focus_sessions_completed"
        )}
        summary.update(SUMMARY_DEFAULTS)
        summary.update(focus_values)
        summary["context_switches"] = len(self.today_data["sessions"])

        for session in self.today_data["sessions"]:
            try:
                duration = float(session.get('duration_minutes', 0) or 0)
            except (TypeError, ValueError):
                duration = 0
            category = str(session.get('category', 'knowledge')).lower()
            pseudo = session.get('is_pseudo_productive', False) or category == 'pseudo_productive'
            if pseudo:
                summary["pseudo_productive"] += duration
            else:
                if category not in ("building", "studying", "applying", "knowledge"):
                    category = "knowledge"
                summary[category] += duration
                summary["total_productive"] += duration

    def replace_activities(self, rows):
        """Replace today's canonical activity timeline with edited table rows."""
        sessions = []
        for row in rows:
            label = str(row.get('label', '')).strip()
            if not label:
                continue
            try:
                duration = round(float(row.get('duration_minutes', 0) or 0), 1)
            except (TypeError, ValueError):
                duration = 0
            category = str(row.get('category', 'Knowledge')).strip() or 'Knowledge'
            sessions.append({
                'start_time': str(row.get('start_time', '')),
                'end_time': str(row.get('end_time', '')),
                'application': label,
                'window_title': label,
                'category': category.title(),
                'duration_minutes': duration,
                'is_pseudo_productive': category.lower() == 'pseudo_productive',
                'source': 'manual',
            })
        with self._lock:
            self._rollover_if_needed()
            self.today_data["sessions"] = sessions
            self._recalculate_activity_summary()
            self.save_today_data()

    def log_focus_session(self, session_data):
        with self._lock:
            self._rollover_if_needed()
            record = session_data.copy()
            record.setdefault('timestamp', self.now_provider().isoformat())
            self.today_data["focus_sessions"].append(record)
            summary = self.today_data["daily_summary"]
            active_minutes = float(record.get('active_minutes', 0) or 0)
            summary["focus_minutes"] += active_minutes
            summary["focus_sessions"] += 1
            if float(record.get('completion_percentage', 0) or 0) >= 100:
                summary["focus_sessions_completed"] += 1
            self.save_today_data()

    def get_focus_sessions(self):
        with self._lock:
            self._rollover_if_needed()
            return [session.copy() for session in self.today_data["focus_sessions"]]

    def get_today_summary(self):
        with self._lock:
            self._rollover_if_needed()
            return self.today_data["daily_summary"].copy()

    def get_day_data(self, date_string=None):
        """Return an isolated day snapshot for analytics."""
        with self._lock:
            self._rollover_if_needed()
            if date_string is None or date_string == self.current_date:
                return json.loads(json.dumps(self.today_data))
            return self._load_date(date_string)

    def get_weekly_data(self, start_date=None):
        if start_date is None:
            today = self.now_provider()
            start_date = today - timedelta(days=today.weekday())
        return [self._load_date((start_date + timedelta(days=i)).strftime('%Y-%m-%d'))
                for i in range(7)]

    def get_monthly_data(self, year=None, month=None):
        if year is None or month is None:
            now = self.now_provider()
            year, month = now.year, now.month
        first_day = datetime(year, month, 1)
        next_month = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)
        days = (next_month - first_day).days
        return [self._load_date((first_day + timedelta(days=i)).strftime('%Y-%m-%d'))
                for i in range(days)]

    def get_recent_activities(self, limit=50):
        with self._lock:
            self._rollover_if_needed()
            activities = []
            for session in self.today_data.get('sessions', [])[-limit:]:
                activities.append({
                    'start_time': session.get('start_time') or session.get('timestamp') or '',
                    'end_time': session.get('end_time', ''),
                    'label': session.get('activity') or session.get('window_title')
                             or session.get('application') or 'Session',
                    'category': session.get('category', 'unknown'),
                    'duration_minutes': session.get('duration_minutes') or session.get('duration', 0),
                })
            return activities
