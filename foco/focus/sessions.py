"""
Focus Manager - Focus sessions and timers
Manages 90min Deep Work and 25min Quick Focus modes
"""
from datetime import datetime
from enum import Enum
from ..config import load_config

class FocusMode(Enum):
    DEEP_WORK = "Deep Work"
    QUICK_FOCUS = "Quick Focus"

class FocusState(Enum):
    INACTIVE = "Inactive"
    RUNNING = "Running"
    PAUSED = "Paused"
    COMPLETED = "Completed"

class FocusManager:
    def __init__(self, data_logger, now_provider=None, config_path="config.json",
                 data_dir="productivity_data"):
        self.data_logger = data_logger
        self.now_provider = now_provider or datetime.now
        self.config_path = config_path
        self.data_dir = data_dir
        self.current_mode = None
        self.state = FocusState.INACTIVE
        self.start_time = None
        self.pause_time = None
        self.total_paused_time = 0
        self.session_data = {}
        
        self.reload_config()

    def reload_config(self):
        """Apply saved focus durations to future sessions."""
        modes = load_config(self.config_path)['focus_modes']
        self.durations = {
            FocusMode.DEEP_WORK: modes['deep_work'],
            FocusMode.QUICK_FOCUS: modes['quick_focus'],
        }
    
    def start_focus_session(self, mode):
        """Start a new focus session with automatic jail mode for Deep Work"""
        if self.state in [FocusState.RUNNING, FocusState.PAUSED]:
            self.end_current_session()
        
        self.current_mode = mode
        self.state = FocusState.RUNNING
        self.start_time = self.now_provider()
        self.pause_time = None
        self.total_paused_time = 0
        
        self.session_data = {
            'mode': mode.value,
            'start_time': self.start_time.strftime('%H:%M:%S'),
            'duration_minutes': self.durations[mode],
            'jail_active': False,
        }
        
        # Automatically enable jail mode for Deep Work sessions
        if mode == FocusMode.DEEP_WORK:
            self._start_jail_mode()
        
        return True
    
    def pause_session(self):
        """Pause the current session"""
        if self.state == FocusState.RUNNING:
            self.state = FocusState.PAUSED
            self.pause_time = self.now_provider()
            return True
        return False
    
    def resume_session(self):
        """Resume a paused session"""
        if self.state == FocusState.PAUSED and self.pause_time:
            self.state = FocusState.RUNNING
            self.total_paused_time += (self.now_provider() - self.pause_time).total_seconds()
            self.pause_time = None
            return True
        return False
    
    def update(self):
        """Update the timer and return current state"""
        if self.state == FocusState.RUNNING:
            current_time = self.now_provider()
            
            # Calculate time considering pauses
            elapsed = (current_time - self.start_time).total_seconds() - self.total_paused_time
            remaining = max(0, (self.durations[self.current_mode] * 60) - elapsed)
            
            if remaining <= 0:
                return self.end_current_session()
            
            # Update session data
            self.session_data.update({
                'elapsed': elapsed,
                'remaining': remaining,
                'elapsed_formatted': self.format_time(elapsed),
                'remaining_formatted': self.format_time(remaining)
            })
            
            return self.session_data.copy()
        
        return None
    
    def end_current_session(self):
        """End the current focus session"""
        if self.state in [FocusState.RUNNING, FocusState.PAUSED]:
            # Always stop jail mode if active when session ends early
            if self.session_data.get('jail_active'):
                self._stop_jail_mode()
            end_time = self.now_provider()
            
            if self.pause_time:  # If paused, add final pause time
                self.total_paused_time += (end_time - self.pause_time).total_seconds()
            
            # Calculate actual work time (excluding pauses)
            total_time = (end_time - self.start_time).total_seconds()
            active_time = total_time - self.total_paused_time
            
            self.session_data.update({
                'end_time': end_time.strftime('%H:%M:%S'),
                'total_minutes': round(total_time / 60, 1),
                'active_minutes': round(active_time / 60, 1),
                'completion_percentage': min(100, round((active_time / 60) / self.durations[self.current_mode] * 100))
            })
            
            # Log the session
            self.log_focus_session()
            
            self.state = FocusState.COMPLETED
            return self.session_data.copy()
        
        return None
    
    def get_remaining_time(self):
        """Get remaining time in current session"""
        if self.state not in [FocusState.RUNNING, FocusState.PAUSED] or not self.start_time:
            return 0
        
        elapsed = self.get_elapsed_time()
        target_seconds = self.durations[self.current_mode] * 60
        remaining = max(0, target_seconds - elapsed)
        
        return remaining
    
    def get_elapsed_time(self):
        """Get elapsed active time in current session"""
        if not self.start_time:
            return 0
        
        if self.state == FocusState.PAUSED:
            return (self.pause_time - self.start_time).total_seconds() - self.total_paused_time
        elif self.state == FocusState.RUNNING:
            return (self.now_provider() - self.start_time).total_seconds() - self.total_paused_time
        elif self.state == FocusState.COMPLETED:
            return float(self.session_data.get('active_minutes', 0)) * 60
        
        return 0
    
    def get_progress_percentage(self):
        """Get progress percentage of current session"""
        if not self.current_mode or not self.start_time:
            return 0
        
        elapsed_minutes = self.get_elapsed_time() / 60
        target_minutes = self.durations[self.current_mode]
        
        return min(100, (elapsed_minutes / target_minutes) * 100)
    
    def get_session_info(self):
        """Get information about current session"""
        if self.state == FocusState.INACTIVE:
            return None
        
        return {
            'mode': self.current_mode.value if self.current_mode else None,
            'state': self.state.value,
            'elapsed_minutes': round(self.get_elapsed_time() / 60, 1),
            'remaining_minutes': round(self.get_remaining_time() / 60, 1),
            'progress_percentage': round(self.get_progress_percentage(), 1),
            'target_minutes': self.durations[self.current_mode] if self.current_mode else 0
        }
    
    def log_focus_session(self):
        """Persist a completed or stopped focus session."""
        if self.session_data:
            self.data_logger.log_focus_session(self.session_data)
            print(f"Focus session completed: {self.session_data['mode']} - "
                  f"{self.session_data.get('active_minutes', 0):.1f}m active")
    
    def _start_jail_mode(self):
        """Start productivity jail mode"""
        try:
            from .blocker import ProductivityEnforcer
            
            self.jail_enforcer = ProductivityEnforcer(
                data_dir=self.data_dir, config_path=self.config_path
            )
            duration_hours = self.durations[self.current_mode] / 60
            
            if self.jail_enforcer.start_enforcement(duration_hours):
                self.session_data['jail_active'] = True
                print(f"Focus jail active for {duration_hours:.1f} hours")
                # Start enforcement monitoring loop in background
                try:
                    self.jail_enforcer.start_monitoring()
                except Exception as mt_err:
                    print(f"Failed to start jail monitor thread: {mt_err}")
            
        except Exception as e:
            print(f"Focus jail failed to start: {e}")
    
    def _stop_jail_mode(self):
        """Stop productivity jail mode"""
        if self.session_data.get('jail_active') and hasattr(self, 'jail_enforcer'):
            try:
                self.jail_enforcer.stop_enforcement()
                self.session_data['jail_active'] = False
                print("Focus jail deactivated")
            except Exception as e:
                print(f"Error stopping focus jail: {e}")
    

    
    def format_time(self, seconds):
        """Format seconds into MM:SS format"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
