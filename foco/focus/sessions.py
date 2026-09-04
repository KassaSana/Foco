"""
Focus Manager - Focus sessions and timers
Manages 90min Deep Work and 25min Quick Focus modes
"""
from datetime import datetime, timedelta
from enum import Enum
import json
import math
from pathlib import Path
from uuid import uuid4
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
                 data_dir="productivity_data", enforcer=None):
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
        self.jail_enforcer = enforcer
        self.last_error = ''
        self.persistence_error = ''
        self.state_file = Path(data_logger.data_dir if data_logger is not None else data_dir) / 'focus_state.json'
        self._save_pending = False
        self._completion_pending = False
        
        self.reload_config()

    def reload_config(self):
        """Apply saved focus durations to future sessions."""
        modes = load_config(self.config_path)['focus_modes']
        self.durations = {
            FocusMode.DEEP_WORK: modes['deep_work'],
            FocusMode.QUICK_FOCUS: modes['quick_focus'],
        }
    
    def start_focus_session(self, mode, intention=''):
        """Start a new focus session with automatic jail mode for Deep Work"""
        self.last_error = ''
        if self.jail_enforcer and (self.jail_enforcer.enforcement_active or self.jail_enforcer.last_error):
            self.last_error = 'Disable the existing block before starting a new focus session.'
            return False
        if self.state in [FocusState.RUNNING, FocusState.PAUSED]:
            self.end_current_session()
        if self._completion_pending or (self.state == FocusState.INACTIVE and self.state_file.exists()):
            self.last_error = 'Resolve the saved focus session before starting another.'
            return False
        
        self.current_mode = mode
        self.state = FocusState.RUNNING
        self.start_time = self.now_provider()
        self.pause_time = None
        self.total_paused_time = 0
        
        self.session_data = {
            'id': uuid4().hex,
            'mode': mode.value,
            'start_time': self.start_time.strftime('%H:%M:%S'),
            'duration_minutes': self.durations[mode],
            'intention': str(intention or '').strip(),
            'jail_active': False,
        }
        
        if not self.save_session_state():
            self.state = FocusState.INACTIVE
            self._save_pending = False
            self.last_error = self.persistence_error
            return False
        # Automatically enable jail mode for Deep Work sessions
        if mode == FocusMode.DEEP_WORK:
            if not self._start_jail_mode():
                self.state = FocusState.INACTIVE
                try:
                    self.state_file.unlink()
                except OSError as error:
                    self.persistence_error = f'Could not clear failed session: {error}'
                return False
        
        return True
    
    def pause_session(self):
        """Pause the current session"""
        if self.state == FocusState.RUNNING:
            if self.session_data.get('jail_active') and not self._stop_jail_mode():
                return False
            self.state = FocusState.PAUSED
            self.pause_time = self.now_provider()
            self.save_session_state()
            return True
        return False
    
    def resume_session(self):
        """Resume a paused session"""
        if self.state == FocusState.PAUSED and self.pause_time:
            if self.current_mode == FocusMode.DEEP_WORK and not self._start_jail_mode():
                return False
            self.state = FocusState.RUNNING
            self.total_paused_time += (self.now_provider() - self.pause_time).total_seconds()
            self.pause_time = None
            self.save_session_state()
            return True
        return False
    
    def update(self):
        """Update the timer and return current state"""
        if self._completion_pending:
            self._persist_completion()
        elif self._save_pending:
            self.save_session_state()
        if self.state == FocusState.RUNNING:
            current_time = self.now_provider()
            
            # Calculate time considering pauses
            elapsed = (current_time - self.start_time).total_seconds() - self.total_paused_time
            remaining = max(0, (self.session_data['duration_minutes'] * 60) - elapsed)
            
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
    
    def end_current_session(self, outcome='Progress', outcome_note=''):
        """End the current focus session"""
        if self.state in [FocusState.RUNNING, FocusState.PAUSED]:
            normalized_outcome = self._normalize_outcome(outcome)
            # Always stop jail mode if active when session ends early
            if self.session_data.get('jail_active'):
                self._stop_jail_mode()
            end_time = self.now_provider()
            if self.state == FocusState.RUNNING:
                deadline = self.start_time + timedelta(
                    seconds=self.total_paused_time + self.session_data['duration_minutes'] * 60
                )
                end_time = min(end_time, deadline)
            
            if self.pause_time:  # If paused, add final pause time
                self.total_paused_time += (end_time - self.pause_time).total_seconds()
            
            # Calculate actual work time (excluding pauses)
            total_time = (end_time - self.start_time).total_seconds()
            active_time = total_time - self.total_paused_time
            
            self.session_data.update({
                'history_date': end_time.strftime('%Y-%m-%d'),
                'end_time': end_time.strftime('%H:%M:%S'),
                'total_minutes': round(total_time / 60, 1),
                'active_minutes': round(active_time / 60, 1),
                'completion_percentage': (
                    100 if active_time >= self.session_data['duration_minutes'] * 60
                    else min(99, round((active_time / 60) / self.session_data['duration_minutes'] * 100))
                ),
                'outcome': normalized_outcome,
                'outcome_note': str(outcome_note or '').strip(),
            })
            
            self.state = FocusState.COMPLETED
            self._completion_pending = True
            self._persist_completion()
            return self.session_data.copy()
        
        return None

    @staticmethod
    def _normalize_outcome(outcome):
        value = str(outcome or 'Progress').strip().title()
        if value not in {'Done', 'Progress', 'Blocked'}:
            raise ValueError('Outcome must be Done, Progress, or Blocked')
        return value
    
    def save_session_state(self):
        """Checkpoint transitions atomically; retry failed writes in update()."""
        payload = {
            'state': self.state.value, 'session': self.session_data,
            'start_time': self.start_time.isoformat(),
            'pause_time': self.pause_time.isoformat() if self.pause_time else None,
            'total_paused_time': self.total_paused_time,
        }
        try:
            temporary = self.state_file.with_suffix('.tmp')
            temporary.write_text(json.dumps(payload, indent=2), encoding='utf-8')
            temporary.replace(self.state_file)
            self._save_pending = False
            self.persistence_error = ''
            return True
        except OSError as error:
            self._save_pending = True
            self.persistence_error = f'Could not save focus state: {error}. Keep Foco open to retry.'
            return False

    def _persist_completion(self):
        # Save the completed record before history so crashes can safely replay it.
        if not self.save_session_state():
            return
        try:
            self.log_focus_session()
            self.state_file.unlink()
            self._completion_pending = False
            self.persistence_error = ''
        except OSError as error:
            self.persistence_error = f'Could not save completed focus: {error}. Keep Foco open to retry.'

    def recover_session(self):
        """Restore after blocker recovery; never silently run unprotected Deep Work."""
        if not self.state_file.exists():
            return False
        try:
            payload = json.loads(self.state_file.read_text(encoding='utf-8'))
            state = FocusState(payload['state'])
            session = payload['session']
            mode = FocusMode(session['mode'])
            target = float(session['duration_minutes'])
            paused = float(payload['total_paused_time'])
            started = datetime.fromisoformat(payload['start_time'])
            pause = datetime.fromisoformat(payload['pause_time']) if payload['pause_time'] else None
            now = self.now_provider()
            if started > now or (pause and pause > now):
                raise ValueError('Saved timer timestamp is in the future')
            elapsed_until_pause = ((pause or now) - started).total_seconds()
            if (state == FocusState.INACTIVE or not isinstance(session.get('id'), str)
                    or not session['id'] or not math.isfinite(target) or target <= 0
                    or not math.isfinite(paused) or paused < 0
                    or started.tzinfo is not None
                    or (pause and (pause.tzinfo is not None or pause < started))
                    or paused > elapsed_until_pause
                    or (state == FocusState.PAUSED and pause is None)):
                raise ValueError('Invalid saved timer')
            if state == FocusState.COMPLETED:
                datetime.strptime(session['history_date'], '%Y-%m-%d')
                for key in ('active_minutes', 'total_minutes', 'completion_percentage'):
                    if not math.isfinite(float(session[key])) or float(session[key]) < 0:
                        raise ValueError('Invalid completed timer')
                if float(session['completion_percentage']) > 100:
                    raise ValueError('Invalid completed timer')
                if float(session['active_minutes']) > target * 60 + 1:
                    raise ValueError('Invalid completed timer')
            session['duration_minutes'] = target
            self.state, self.current_mode = state, mode
            self.session_data = session
            self.start_time, self.pause_time = started, pause
            self.total_paused_time = paused
            self._completion_pending = state == FocusState.COMPLETED
            if mode == FocusMode.DEEP_WORK:
                enforcer = self.get_enforcer()
                self.session_data['jail_active'] = enforcer.enforcement_active
                if state == FocusState.RUNNING and self.get_remaining_time() > 0 and not enforcer.enforcement_active:
                    self.state = FocusState.PAUSED
                    self.pause_time = self.now_provider()
                    self.last_error = 'Recovered focus is paused. Resume to restore blocking.'
                    self.save_session_state()
            self.update()
            return True
        except (OSError, ValueError, TypeError, KeyError, AttributeError, OverflowError) as error:
            self.persistence_error = f'Could not recover focus: {error}. Saved state was preserved.'
            return False

    def shutdown(self):
        """Checkpoint an active session and remove all blocking before exit."""
        self.last_error = ''
        if self.state == FocusState.RUNNING:
            self.pause_session()
        if self.state in (FocusState.RUNNING, FocusState.PAUSED):
            if self._save_pending:
                self.save_session_state()
            if self._save_pending:
                self.last_error = self.persistence_error
                return False
        enforcer = self.jail_enforcer
        if enforcer and (enforcer.enforcement_active or enforcer.has_block_entries()):
            if not enforcer.stop_enforcement():
                self.last_error = enforcer.last_error or 'Could not remove blocking. Retry Disable.'
                return False
            self.session_data['jail_active'] = False
        return True

    def discard_saved_session(self):
        """Remove a saved focus checkpoint after the user confirms recovery is impossible."""
        enforcer = self.jail_enforcer
        if enforcer and (enforcer.enforcement_active or enforcer.has_block_entries()):
            self.last_error = 'Disable blocking before clearing the saved focus session.'
            return False
        try:
            if self.state_file.exists():
                self.state_file.unlink()
            self.current_mode = None
            self.state = FocusState.INACTIVE
            self.start_time = None
            self.pause_time = None
            self.total_paused_time = 0
            self.session_data = {}
            self._save_pending = False
            self._completion_pending = False
            self.persistence_error = ''
            self.last_error = ''
            return True
        except OSError as error:
            self.last_error = f'Could not clear saved focus session: {error}'
            return False

    def get_remaining_time(self):
        """Get remaining time in current session"""
        if self.state not in [FocusState.RUNNING, FocusState.PAUSED] or not self.start_time:
            return 0
        
        elapsed = self.get_elapsed_time()
        target_seconds = self.session_data['duration_minutes'] * 60
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
        target_minutes = self.session_data['duration_minutes']
        
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
            'remaining_seconds': self.get_remaining_time(),
            'progress_percentage': round(self.get_progress_percentage(), 1),
            'target_minutes': self.session_data['duration_minutes'] if self.current_mode else 0
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
            enforcer = self.get_enforcer()
            duration_hours = self.get_remaining_time() / 3600
            
            if enforcer.start_enforcement(duration_hours):
                self.session_data['jail_active'] = True
                print(f"Focus jail active for {duration_hours:.1f} hours")
                # Start enforcement monitoring loop in background
                try:
                    self.jail_enforcer.start_monitoring()
                except Exception as mt_err:
                    self._stop_jail_mode()
                    self.last_error = f'Could not start blocking monitor: {mt_err}'
                    return False
                self.last_error = ''
                return True
            self.session_data['jail_active'] = enforcer.enforcement_active
            self.last_error = enforcer.last_error
            
        except Exception as e:
            self.last_error = f'Focus blocking failed to start: {e}'
            print(f"Focus jail failed to start: {e}")
        return False

    def get_enforcer(self):
        """Share one blocking owner with the manual controls and recovery flow."""
        if self.jail_enforcer is None:
            from .blocker import ProductivityEnforcer
            self.jail_enforcer = ProductivityEnforcer(
                data_dir=self.data_dir, config_path=self.config_path
            )
        return self.jail_enforcer
    
    def _stop_jail_mode(self):
        """Stop productivity jail mode"""
        if self.session_data.get('jail_active') and self.jail_enforcer:
            try:
                if not self.jail_enforcer.stop_enforcement():
                    self.last_error = self.jail_enforcer.last_error
                    return False
                self.session_data['jail_active'] = False
                self.last_error = ''
                print("Focus jail deactivated")
            except Exception as e:
                self.last_error = f'Could not remove focus blocking: {e}'
                print(f"Error stopping focus jail: {e}")
                return False
        return True
    

    
    def format_time(self, seconds):
        """Format seconds into MM:SS format"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
