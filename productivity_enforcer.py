"""
Productivity Enforcer - Website and Application Blocker
Blocks distracting websites and applications during work sessions
"""
import os
import sys
import subprocess
import json
from datetime import datetime, timedelta
from pathlib import Path
import winreg
import ctypes
from ctypes import wintypes
import time
import threading

class ProductivityEnforcer:
    BLOCK_START = "# FOCO PRODUCTIVITY BLOCKER START"
    BLOCK_END = "# FOCO PRODUCTIVITY BLOCKER END"
    LEGACY_MARKER = "# PRODUCTIVITY_BLOCKER"

    def __init__(self, hosts_file=None, data_dir="productivity_data", flush_dns=True):
        self.hosts_file = str(hosts_file or r"C:\Windows\System32\drivers\etc\hosts")
        self.data_dir = Path(data_dir)
        self.hosts_backup = self.data_dir / "hosts_backup.txt"
        self.state_file = self.data_dir / "enforcement_state.json"
        self.flush_dns = flush_dns
        self.blocked_processes = []
        self.enforcement_active = False
        self._monitor_thread = None
        
        # Ensure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.load_block_config()
    
    def load_block_config(self):
        """Load blocking configuration"""
        self.blocked_sites = [
            # Social Media
            "facebook.com", "www.facebook.com", "m.facebook.com",
            "twitter.com", "www.twitter.com", "x.com", "www.x.com",
            "instagram.com", "www.instagram.com",
            "tiktok.com", "www.tiktok.com",
            "snapchat.com", "www.snapchat.com",
            "discord.com", "www.discord.com",
            
            # Entertainment/Distractions
            "reddit.com", "www.reddit.com", "old.reddit.com", "new.reddit.com",
            "9gag.com", "www.9gag.com",
            "buzzfeed.com", "www.buzzfeed.com",
            "imgur.com", "www.imgur.com",
            
            # Most of YouTube (with exceptions)
            "youtube.com", "www.youtube.com", "m.youtube.com",
            
            # Gaming
            "steam.com", "store.steampowered.com",
            "twitch.tv", "www.twitch.tv",
            "epic games.com", "www.epicgames.com",
            
            # News/Time wasters
            "cnn.com", "www.cnn.com",
            "bbc.com", "www.bbc.com",
            "news.ycombinator.com",
            
            # Shopping
            "amazon.com", "www.amazon.com", "shopping.amazon.com",
            "ebay.com", "www.ebay.com",
            "aliexpress.com", "www.aliexpress.com"
        ]
        
        # YouTube channels/creators that ARE allowed (educational)
        self.allowed_youtube = [
            "neetcode", "neetcodeio",
            "mit", "stanford", "harvard", "berkeley",
            "freecodecamp", "codecademy", "coursera",
            "khan academy", "khanacademy",
            "programming with mosh", "traversy media",
            "tech with tim", "corey schafer",
            "sentdex", "derek banas",
            "cs50", "computerphile", "numberphile",
            "3blue1brown", "ben eater",
            "computerscience", "algorithms",
            "lectures", "tutorial", "course",
            "learn", "education", "university"
        ]
        
        # Applications to block
        self.blocked_apps = [
            # Gaming
            "steam.exe", "steamwebhelper.exe",
            "epicgameslauncher.exe", "epicgames.exe",
            "origin.exe", "originwebhelperservice.exe",
            "battlenet.exe", "battle.net.exe",
            "riotclientservices.exe", "valorant.exe", "leagueoflegends.exe",
            "minecraft.exe", "minecraftlauncher.exe",
            
            # Entertainment
            "spotify.exe", "spotifywebhelper.exe",
            "netflix.exe", "hulu.exe", "disney+.exe",
            "vlc.exe", "mediaplayer.exe",
            
            # Social Media Desktop Apps
            "discord.exe", "slack.exe", "teams.exe",
            "whatsapp.exe", "telegram.exe",
            
            # Other Distractions
            "torrent.exe", "utorrent.exe", "bittorrent.exe"
        ]
        
        # Always allowed applications (work tools)
        self.allowed_apps = [
            "code.exe", "devenv.exe", "idea64.exe", "pycharm64.exe",
            "cmd.exe", "powershell.exe", "terminal.exe",
            "git.exe", "node.exe", "python.exe", "java.exe",
            "notepad.exe", "notepad++.exe",
            "chrome.exe", "firefox.exe", "edge.exe",  # Browsers (with site filtering)
            "explorer.exe", "taskmgr.exe"
        ]
    
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
            print(f"⚠️ Could not flush DNS cache: {e}")

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
    
    def check_youtube_content(self, title):
        """Check if YouTube content is educational/allowed"""
        if not title:
            return False
        
        title_lower = title.lower()
        
        # Check for allowed creators/channels
        for allowed in self.allowed_youtube:
            if allowed.lower() in title_lower:
                return True
        
        # Block common entertainment keywords
        blocked_keywords = [
            "funny", "meme", "react", "reaction", "prank", "fail",
            "tiktok", "shorts", "vlog", "lifestyle", "drama",
            "gaming", "gameplay", "stream", "highlights",
            "music video", "song", "album", "concert"
        ]
        
        for blocked in blocked_keywords:
            if blocked in title_lower:
                return False
        
        return False  # Block by default unless explicitly allowed
    
    def monitor_processes(self):
        """Monitor and kill blocked processes"""
        try:
            import psutil
            
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    proc_name = proc.info['name'].lower()
                    
                    if proc_name in [app.lower() for app in self.blocked_apps]:
                        print(f"🚫 Blocking {proc_name} (PID: {proc.info['pid']})")
                        proc.terminate()  # Terminate the process
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
                    
        except ImportError:
            print("⚠️ psutil not available for process monitoring")
    
    def check_browser_content(self):
        """Monitor browser windows for blocked content"""
        try:
            import win32gui
            
            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    window_text = win32gui.GetWindowText(hwnd)
                    if window_text:
                        windows.append(window_text)
            
            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)
            
            for window_title in windows:
                title_lower = window_title.lower()
                
                # Check for blocked sites in browser titles
                for site in self.blocked_sites:
                    if site in title_lower:
                        # Special handling for YouTube
                        if "youtube" in title_lower:
                            if not self.check_youtube_content(window_title):
                                print(f"🚫 Blocked YouTube content: {window_title[:50]}...")
                                self.show_block_message("YouTube content blocked", 
                                                       "Only educational content allowed!")
                        else:
                            print(f"🚫 Blocked site detected: {site}")
                            self.show_block_message("Website blocked", f"{site} is not allowed during work time")
                            
        except ImportError:
            print("⚠️ win32gui not available for browser monitoring")
    
    def show_block_message(self, title, message):
        """Show blocking notification"""
        try:
            import tkinter as tk
            from tkinter import messagebox
            
            root = tk.Tk()
            root.withdraw()  # Hide main window
            messagebox.showwarning(title, f"{message}\n\nFocus on your work! 💪")
            root.destroy()
            
        except Exception:
            print(f"🚫 {title}: {message}")
    
    def start_enforcement(self, duration_hours=8):
        """Start productivity enforcement"""
        print("🔒 Starting Productivity Enforcement Mode")
        print("=" * 50)
        
        if not self.backup_hosts_file():
            return False
        
        if not self.modify_hosts_file(block=True):
            return False
        
        self.enforcement_active = True
        end_time = datetime.now() + timedelta(hours=duration_hours)
        
        print(f"✅ Enforcement active until: {end_time.strftime('%I:%M %p')}")
        print("\n📋 What's blocked:")
        print("❌ Social media (Reddit, Twitter, Facebook, etc.)")
        print("❌ Entertainment YouTube (only educational allowed)")
        print("❌ Gaming platforms and games")
        print("❌ News and shopping sites")
        print("❌ Messaging apps")
        
        print("\n📋 What's allowed:")
        print("✅ Programming tools (VS Code, IDEs, terminals)")
        print("✅ Educational content (NeetCode, lectures, courses)")
        print("✅ Work websites (GitHub, Stack Overflow, documentation)")
        print("✅ GeeksforGeeks and learning platforms")
        
        # Save enforcement state
        self.save_enforcement_state(end_time)
        
        return True
    
    def stop_enforcement(self):
        """Stop productivity enforcement"""
        print("Stopping Productivity Enforcement Mode")
        
        if self.modify_hosts_file(block=False):
            self.enforcement_active = False
            self.clear_enforcement_state()
            print("All restrictions removed")
            return True
        
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
        """Resume a live jail or clean up stale blocking after a restart."""
        end_time = self.load_enforcement_state()
        if end_time is None:
            if self.has_block_entries():
                self.modify_hosts_file(block=False)
            return None

        if datetime.now() >= end_time:
            self.enforcement_active = True
            self.stop_enforcement()
            return None

        self.enforcement_active = True
        if not self.has_block_entries() and not self.modify_hosts_file(block=True):
            self.enforcement_active = False
            return None
        return end_time

    def start_monitoring(self):
        """Start one daemon monitor thread for the current enforcement period."""
        if self._monitor_thread and self._monitor_thread.is_alive():
            return self._monitor_thread
        self._monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self._monitor_thread.start()
        return self._monitor_thread
    
    def monitor_loop(self):
        """Main monitoring loop"""
        print("👁️ Starting productivity monitoring...")
        
        try:
            while self.enforcement_active:
                # Check if enforcement time has expired
                end_time = self.load_enforcement_state()
                if end_time is None or datetime.now() >= end_time:
                    print("Enforcement period ended")
                    self.stop_enforcement()
                    break
                
                # Monitor processes and browser content
                self.monitor_processes()
                self.check_browser_content()
                
                time.sleep(5)  # Check every 5 seconds
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
        except Exception as e:
            print(f"❌ Error in monitoring loop: {e}")

def main():
    """Main function"""
    print("🔒 ADHD Productivity Enforcer")
    print("=" * 40)
    print("Turn your laptop into a focused work machine!")
    
    # Check admin privileges
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
            print("❌ Administrator privileges required!")
            print("Right-click and 'Run as Administrator'")
            input("Press Enter to exit...")
            return
    except:
        pass
    
    enforcer = ProductivityEnforcer()
    
    # Check if enforcement is already active
    end_time = enforcer.load_enforcement_state()
    if end_time:
        print(f"⚠️ Enforcement already active until: {end_time.strftime('%I:%M %p')}")
        choice = input("Continue monitoring? (y/n): ").lower().strip()
        if choice in ['y', 'yes']:
            enforcer.enforcement_active = True
            enforcer.monitor_loop()
            return
    
    print("\n📋 Options:")
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
            print("❌ Invalid number")
    elif choice == '5':
        enforcer.stop_enforcement()
    elif choice == '6':
        print("Goodbye! 👋")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
