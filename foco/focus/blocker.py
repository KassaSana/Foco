"""Foco website and application blocking service."""
import os
import subprocess
import json
from datetime import datetime, timedelta
from pathlib import Path
import ctypes
import time
import threading
from ..config import load_config

class ProductivityEnforcer:
    BLOCK_START = "# FOCO PRODUCTIVITY BLOCKER START"
    BLOCK_END = "# FOCO PRODUCTIVITY BLOCKER END"
    LEGACY_MARKER = "# PRODUCTIVITY_BLOCKER"

    def __init__(self, hosts_file=None, data_dir="productivity_data", flush_dns=True,
                 config_path="config.json"):
        self.hosts_file = str(hosts_file or r"C:\Windows\System32\drivers\etc\hosts")
        self.data_dir = Path(data_dir)
        self.hosts_backup = self.data_dir / "hosts_backup.txt"
        self.state_file = self.data_dir / "enforcement_state.json"
        self.flush_dns = flush_dns
        self.config_path = config_path
        self.enforcement_active = False
        self.last_error = ''
        self._lock = threading.RLock()
        self._monitor_thread = None
        
        # Ensure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.load_block_config()
    
    def load_block_config(self):
        """Load blocking configuration"""
        config = load_config(self.config_path)
        self.blocked_sites = config['blocked_sites']
        self.blocked_apps = config['blocked_apps']
    
    def backup_hosts_file(self):
        """Back up the clean hosts file once without overwriting that safety copy."""
        try:
            if self.hosts_backup.exists():
                return True
            if os.path.exists(self.hosts_file):
                with open(self.hosts_file, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                with open(self.hosts_backup, 'w', encoding='utf-8') as f:
                    f.write(content)
                print("Hosts file backed up")
                return True
        except Exception as e:
            print(f"Error backing up hosts file: {e}")
            return False
    
    def _without_foco_entries(self, lines):
        """Remove Foco-managed entries while preserving every user-managed line."""
        cleaned = []
        inside_block = False
        for line in lines:
            stripped = line.strip()
            if stripped == self.BLOCK_START:
                inside_block = True
                continue
            if stripped == self.BLOCK_END:
                inside_block = False
                continue
            if inside_block:
                continue
            if stripped.endswith(self.LEGACY_MARKER):
                continue
            if stripped == "# PRODUCTIVITY BLOCKER - DO NOT EDIT BELOW THIS LINE":
                continue
            cleaned.append(line)
        return cleaned

    def has_block_entries(self):
        """Return whether the hosts file contains Foco-managed entries."""
        try:
            with open(self.hosts_file, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            return self.BLOCK_START in content or self.LEGACY_MARKER in content
        except OSError:
            return False

    def _flush_dns(self):
        if not self.flush_dns:
            return
        try:
            subprocess.run(["ipconfig", "/flushdns"], capture_output=True, check=False)
        except OSError as e:
            print(f"Could not flush DNS cache: {e}")

    def modify_hosts_file(self, block=True):
        """Modify hosts file to block/unblock websites"""
        try:
            # Read current hosts file
            with open(self.hosts_file, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
            
            lines = self._without_foco_entries(lines)
            
            if block:
                if lines and not lines[-1].endswith('\n'):
                    lines[-1] += '\n'
                lines.extend(["\n", f"{self.BLOCK_START}\n"])
                for site in self.blocked_sites:
                    lines.append(f"127.0.0.1 {site}\n")
                lines.append(f"{self.BLOCK_END}\n")
            
            # Write back to hosts file
            with open(self.hosts_file, 'w', encoding='utf-8', newline='') as f:
                f.writelines(lines)
            
            self._flush_dns()
            
            action = "blocked" if block else "unblocked"
            print(f"Websites {action}")
            return True
            
        except Exception as e:
            print(f"Error modifying hosts file: {e}")
            print("Make sure you're running as administrator!")
            return False
    
    def monitor_processes(self):
        """Monitor and kill blocked processes"""
        try:
            import psutil
            
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    proc_name = proc.info['name'].lower()
                    
                    if proc_name in [app.lower() for app in self.blocked_apps]:
                        print(f"Blocking {proc_name} (PID: {proc.info['pid']})")
                        proc.terminate()  # Terminate the process
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
                    
        except ImportError:
            print("psutil is not available for process monitoring")
    
    def start_enforcement(self, duration_hours=8):
        with self._lock:
            return self._start_enforcement(duration_hours)

    def _start_enforcement(self, duration_hours):
        """Start productivity enforcement"""
        self.last_error = ''
        if self.enforcement_active:
            self.last_error = 'Blocking is already active. Disable it before starting another block.'
            return False
        self.load_block_config()
        print("Starting Foco focus jail")
        print("=" * 50)
        
        if not self.backup_hosts_file():
            self.last_error = 'Could not back up the hosts file. Blocking was not started.'
            return False
        
        if not self.modify_hosts_file(block=True):
            self.last_error = 'Could not apply blocking. Check administrator access and retry.'
            return False
        
        self.enforcement_active = True
        end_time = datetime.now() + timedelta(hours=duration_hours)
        
        print(f"Enforcement active until: {end_time.strftime('%I:%M %p')}")
        print(f"Blocking {len(self.blocked_sites)} domains and {len(self.blocked_apps)} applications.")
        
        # Save enforcement state
        try:
            self.save_enforcement_state(end_time)
        except OSError as error:
            # Undo the hosts change if its recovery state cannot be saved.
            removed = self.stop_enforcement()
            self.last_error = (
                f'Could not save blocking state: {error}. '
                + ('Blocking was removed.' if removed else 'Blocking may remain; retry Disable.')
            )
            return False
        
        return True
    
    def stop_enforcement(self):
        with self._lock:
            return self._stop_enforcement()

    def _stop_enforcement(self):
        """Stop productivity enforcement"""
        self.last_error = ''
        print("Stopping Productivity Enforcement Mode")
        
        if self.modify_hosts_file(block=False):
            self.enforcement_active = False
            try:
                self.clear_enforcement_state()
            except OSError as error:
                self.last_error = f'Blocking removed, but recovery state could not be cleared: {error}. Retry Disable.'
                return False
            print("All restrictions removed")
            return True
        
        self.last_error = 'Could not remove blocking. Check administrator access and retry Disable.'
        return False
    
    def save_enforcement_state(self, end_time):
        """Save current enforcement state"""
        state = {
            'active': True,
            'end_time': end_time.isoformat(),
            'started': datetime.now().isoformat()
        }
        
        temp_file = self.state_file.with_suffix('.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)
        temp_file.replace(self.state_file)
    
    def load_enforcement_state(self):
        """Return the saved end time, including an already-expired end time."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                
                if state.get('active'):
                    return datetime.fromisoformat(state['end_time'])
                
            except Exception as e:
                print(f"Error loading enforcement state: {e}")
        
        return None
    
    def clear_enforcement_state(self):
        """Clear enforcement state file"""
        if self.state_file.exists():
            self.state_file.unlink()

    def recover_enforcement(self):
        with self._lock:
            return self._recover_enforcement()

    def _recover_enforcement(self):
        """Resume a live jail or clean up stale blocking after a restart."""
        self.last_error = ''
        end_time = self.load_enforcement_state()
        if end_time is None:
            if self.has_block_entries():
                self.enforcement_active = True
                self.stop_enforcement()
            return None

        if datetime.now() >= end_time:
            self.enforcement_active = True
            self.stop_enforcement()
            return None

        self.enforcement_active = True
        if not self.has_block_entries() and not self.modify_hosts_file(block=True):
            self.enforcement_active = False
            self.last_error = 'Could not restore blocking. Check administrator access and retry.'
            return None
        return end_time

    def start_monitoring(self):
        """Start one daemon monitor thread for the current enforcement period."""
        with self._lock:
            if self._monitor_thread and self._monitor_thread.is_alive():
                return self._monitor_thread
            self._monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
            self._monitor_thread.start()
            return self._monitor_thread
    
    def monitor_loop(self):
        """Main monitoring loop"""
        print("Starting focus jail monitoring...")
        
        try:
            while True:
                # Check if enforcement time has expired
                with self._lock:
                    if not self.enforcement_active:
                        self._monitor_thread = None
                        break
                    end_time = self.load_enforcement_state()
                    if end_time is None or datetime.now() >= end_time:
                        print("Enforcement period ended")
                        if self.stop_enforcement():
                            self._monitor_thread = None
                            break
                    else:
                        # Never terminate processes after expiry, even if cleanup fails.
                        self.monitor_processes()
                
                time.sleep(5)  # Check every 5 seconds
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
        except Exception as e:
            self.last_error = f'Blocking monitor stopped: {e}. Retry Disable.'
            print(f"Error in monitoring loop: {e}")

def main():
    """Main function"""
    print("Foco Focus Jail")
    print("=" * 40)
    print("Turn your laptop into a focused work machine!")
    
    # Check admin privileges
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
            print("Administrator privileges required.")
            print("Right-click and 'Run as Administrator'")
            input("Press Enter to exit...")
            return
    except:
        pass
    
    enforcer = ProductivityEnforcer()
    
    # Check if enforcement is already active
    end_time = enforcer.recover_enforcement()
    if end_time:
        print(f"Enforcement already active until: {end_time.strftime('%I:%M %p')}")
        choice = input("Continue monitoring? (y/n): ").lower().strip()
        if choice in ['y', 'yes']:
            enforcer.enforcement_active = True
            enforcer.monitor_loop()
            return
    
    print("\nOptions:")
    print("1. Start 8-hour work session")
    print("2. Start 4-hour study session") 
    print("3. Start 2-hour focus session")
    print("4. Custom duration")
    print("5. Stop enforcement")
    print("6. Exit")
    
    choice = input("\nEnter choice (1-6): ").strip()
    
    if choice == '1':
        if enforcer.start_enforcement(8):
            enforcer.monitor_loop()
    elif choice == '2':
        if enforcer.start_enforcement(4):
            enforcer.monitor_loop()
    elif choice == '3':
        if enforcer.start_enforcement(2):
            enforcer.monitor_loop()
    elif choice == '4':
        try:
            hours = float(input("Enter hours: "))
            if enforcer.start_enforcement(hours):
                enforcer.monitor_loop()
        except ValueError:
            print("Invalid number")
    elif choice == '5':
        enforcer.stop_enforcement()
    elif choice == '6':
        print("Goodbye")
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
