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

class ProductivityEnforcer:
    def __init__(self):
        self.hosts_file = r"C:\Windows\System32\drivers\etc\hosts"
        self.hosts_backup = Path("productivity_data") / "hosts_backup.txt"
        self.blocked_processes = []
        self.enforcement_active = False
        
        # Ensure data directory exists
        Path("productivity_data").mkdir(exist_ok=True)
        
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
        """Backup original hosts file"""
        try:
            if os.path.exists(self.hosts_file):
                with open(self.hosts_file, 'r') as f:
                    content = f.read()
                with open(self.hosts_backup, 'w') as f:
                    f.write(content)
                print("✅ Hosts file backed up")
                return True
        except Exception as e:
            print(f"❌ Error backing up hosts file: {e}")
            return False
    
    def modify_hosts_file(self, block=True):
        """Modify hosts file to block/unblock websites"""
        try:
            # Read current hosts file
            with open(self.hosts_file, 'r') as f:
                lines = f.readlines()
            
            # Remove existing productivity blocker entries
            lines = [line for line in lines if not line.strip().endswith("# PRODUCTIVITY_BLOCKER")]
            
            if block:
                # Add blocking entries
                lines.append("\n# PRODUCTIVITY BLOCKER - DO NOT EDIT BELOW THIS LINE\n")
                for site in self.blocked_sites:
                    lines.append(f"127.0.0.1 {site} # PRODUCTIVITY_BLOCKER\n")
            
            # Write back to hosts file
            with open(self.hosts_file, 'w') as f:
                f.writelines(lines)
            
            # Flush DNS cache
            subprocess.run(["ipconfig", "/flushdns"], capture_output=True)
            
            action = "blocked" if block else "unblocked"
            print(f"✅ Websites {action}")
            return True
            
        except Exception as e:
            print(f"❌ Error modifying hosts file: {e}")
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
        print("🔓 Stopping Productivity Enforcement Mode")
        
        if self.modify_hosts_file(block=False):
            self.enforcement_active = False
            self.clear_enforcement_state()
            print("✅ All restrictions removed")
            return True
        
        return False
    
    def save_enforcement_state(self, end_time):
        """Save current enforcement state"""
        state = {
            'active': True,
            'end_time': end_time.isoformat(),
            'started': datetime.now().isoformat()
        }
        
        with open(Path("productivity_data") / "enforcement_state.json", 'w') as f:
            json.dump(state, f, indent=2)
    
    def load_enforcement_state(self):
        """Load enforcement state"""
        state_file = Path("productivity_data") / "enforcement_state.json"
        
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    state = json.load(f)
                
                if state.get('active'):
                    end_time = datetime.fromisoformat(state['end_time'])
                    if datetime.now() < end_time:
                        self.enforcement_active = True
                        return end_time
                
            except Exception as e:
                print(f"Error loading enforcement state: {e}")
        
        return None
    
    def clear_enforcement_state(self):
        """Clear enforcement state file"""
        state_file = Path("productivity_data") / "enforcement_state.json"
        if state_file.exists():
            state_file.unlink()
    
    def monitor_loop(self):
        """Main monitoring loop"""
        print("👁️ Starting productivity monitoring...")
        
        try:
            while self.enforcement_active:
                # Check if enforcement time has expired
                end_time = self.load_enforcement_state()
                if end_time and datetime.now() >= end_time:
                    print("⏰ Enforcement period ended")
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