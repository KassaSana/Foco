# Foco - Technical Cheatsheet & Deep Dive

## 🎯 Quick Summary (30 seconds)
**Foco** is a Windows-based ADHD productivity tracker built in Python that:
- **Monitors** 50+ apps using Win32 APIs to track real-time activity
- **Blocks** 40+ distracting websites/apps via hosts file modification + process termination
- **Categorizes** work into Building/Studying/Applying/Knowledge with pseudo-productive detection
- **Visualizes** productivity with Tkinter dashboard showing daily/weekly/monthly/yearly analytics
- **Enforces** focus with 90-min Deep Work and 25-min Pomodoro modes with automatic "jail" blocking

**Tech Stack:** Python, Tkinter (GUI), psutil (process monitoring), Win32 APIs (window detection), matplotlib (analytics), JSON (persistence)

**Scale:** 2,718 LOC, tracked 1,000+ events per session, used by UF students

---

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     main.py (Entry Point)                   │
│  ProductivityTracker: Initializes all components + GUI loop │
└──────────────┬──────────────────────────────────────────────┘
               │
       ┌───────┴────────┬─────────────┬─────────────────┐
       ▼                ▼             ▼                 ▼
┌─────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Dashboard  │  │   Activity   │  │ Data Logger  │  │    Focus     │
│  (Tkinter)  │  │   Monitor    │  │   (JSON)     │  │   Manager    │
│  3 Tabs     │  │  Win32 APIs  │  │  Persistence │  │  Timers      │
└──────┬──────┘  └──────┬───────┘  └──────────────┘  └──────┬───────┘
       │                │                                    │
       ▼                ▼                                    ▼
┌─────────────┐  ┌──────────────┐                   ┌──────────────┐
│   Stats     │  │  Category    │                   │ Productivity │
│ Calculator  │  │   Engine     │                   │  Enforcer    │
│   Weekly/   │  │  Smart AI    │                   │ Hosts Block  │
│  Monthly    │  │Categorization│                   │Process Kill  │
└─────────────┘  └──────────────┘                   └──────────────┘
```

### Data Flow:
1. **ActivityMonitor** polls active window every 1s → gets app name + window title
2. **CategoryEngine** classifies activity → Building/Studying/Applying/Knowledge
3. **DataLogger** persists sessions → JSON files (one per day)
4. **Dashboard** refreshes every 2s → displays real-time stats
5. **FocusManager** handles timers → auto-enables "jail mode" for Deep Work
6. **ProductivityEnforcer** modifies hosts file → blocks distractions

---

## 📦 Module Breakdown (Deep Dive)

### 1. **main.py** - Application Entry Point
**Purpose:** Orchestrates the entire application, starts GUI and background monitoring

```python
class ProductivityTracker:
    def __init__(self):
        self.root = tk.Tk()  # Main Tkinter window
        self.data_logger = DataLogger()
        self.activity_monitor = ActivityMonitor(self.data_logger)
        self.dashboard = ProductivityDashboard(self.root, self.data_logger, self.activity_monitor)
        
        # Background monitoring thread (daemon=True means dies when main thread dies)
        self.monitor_thread = threading.Thread(target=self.start_monitoring, daemon=True)
        self.monitor_thread.start()
    
    def start_monitoring(self):
        while self.monitoring:
            self.activity_monitor.update()  # Poll every second
            time.sleep(1)
```

**Key Design Decision:** Background thread for monitoring prevents GUI blocking. Daemon thread ensures clean shutdown.

---

### 2. **activity_monitor.py** - Real-Time Activity Detection
**Purpose:** Tracks active window, detects idle time, logs application sessions

**Core APIs:**
```python
# Win32 APIs for window tracking
import win32gui
import win32process
import psutil

def get_active_window_info(self):
    hwnd = win32gui.GetForegroundWindow()  # Get active window handle
    window_title = win32gui.GetWindowText(hwnd)  # Get window title
    _, pid = win32process.GetWindowThreadProcessId(hwnd)  # Get process ID
    process = psutil.Process(pid)  # Get process details
    return process.name(), window_title
```

**Session Tracking:**
- Detects app switches → logs previous session duration
- Tracks idle time (5-min threshold via CPU monitoring)
- Minimum session length: 30 seconds (filters noise)

**Example Session Data:**
```python
{
    'start_time': '14:30:22',
    'end_time': '14:45:30',
    'application': 'code.exe',
    'window_title': 'main.py - Visual Studio Code',
    'category': 'Building',
    'duration_minutes': 15.1,
    'is_pseudo_productive': False
}
```

---

### 3. **category_engine.py** - Smart Activity Categorization
**Purpose:** Classifies activities using keyword matching and pattern recognition

**Categories:**
1. **Building** - Coding, development (VS Code, PyCharm, terminals)
2. **Studying** - Educational content (PDFs, Canvas, Coursera)
3. **Applying** - Job search (LinkedIn jobs, Indeed, Glassdoor)
4. **Knowledge** - Learning/research (Stack Overflow, documentation, GitHub)

**Pseudo-Productive Detection:**
```python
def is_pseudo_productive(self, app_name, window_title):
    # YouTube programming videos (watching instead of doing)
    if 'youtube' in window_title:
        if any(kw in window_title for kw in ['programming', 'coding', 'tutorial']):
            return True  # 🚨 Watching tutorials ≠ actual work
    
    # LinkedIn feed scrolling (not job applications)
    if 'linkedin' in window_title:
        if not any(kw in window_title for kw in ['job', 'apply', 'message']):
            return True  # 🚨 Social networking, not applying
    
    # Reddit, Twitter, Facebook → always pseudo-productive
    return any(site in window_title for site in ['reddit', 'twitter', 'facebook'])
```

**Configuration (config.json):**
```json
{
  "focus_modes": {"deep_work": 90, "quick_focus": 25},
  "building_apps": ["code.exe", "idea64.exe", "pycharm64.exe"],
  "studying_apps": ["canvas", "pdf", "notion", "onenote"],
  "pseudo_productive_sites": ["youtube.com", "reddit.com", "twitter.com"]
}
```

---

### 4. **data_logger.py** - Local Persistence
**Purpose:** Saves/loads productivity data using JSON files

**File Structure:**
```
productivity_data/
├── 2024-01-15.json  # Daily data files
├── 2024-01-16.json
├── enforcement_state.json  # Jail mode state
└── hosts_backup.txt  # Original hosts file
```

**Daily Data Format:**
```json
{
  "date": "2024-01-15",
  "sessions": [
    {"start_time": "09:00", "application": "code.exe", "category": "Building", "duration_minutes": 45.2},
    {"start_time": "10:00", "application": "chrome.exe", "category": "Knowledge", "duration_minutes": 12.5}
  ],
  "daily_summary": {
    "building": 120.5,
    "studying": 45.0,
    "applying": 30.0,
    "knowledge": 60.0,
    "pseudo_productive": 25.0,
    "context_switches": 23,
    "total_productive": 255.5
  }
}
```

**Key Methods:**
```python
def start_session(session_data):  # Called on app switch
def end_session(session_data):    # Log completed session
def get_today_summary():          # Return daily totals
def get_weekly_data():            # Return 7-day array
def get_monthly_data():           # Return monthly array
```

---

### 5. **focus_manager.py** - Timer & Focus Sessions
**Purpose:** Manages Pomodoro (25 min) and Deep Work (90 min) sessions with automatic jail mode

**Focus Modes:**
```python
class FocusMode(Enum):
    DEEP_WORK = "Deep Work"      # 90 minutes, auto-jail
    QUICK_FOCUS = "Quick Focus"  # 25 minutes, no jail

class FocusState(Enum):
    INACTIVE = "Inactive"
    RUNNING = "Running"
    PAUSED = "Paused"
    COMPLETED = "Completed"
```

**Session Flow:**
```python
def start_focus_session(self, mode):
    self.start_time = datetime.now()
    # Auto-enable jail mode for Deep Work
    if mode == FocusMode.DEEP_WORK:
        self._start_jail_mode()  # Block distractions automatically
    
def update(self):
    # Calculate remaining time
    elapsed = (datetime.now() - self.start_time).total_seconds() - self.total_paused_time
    remaining = (self.durations[self.current_mode] * 60) - elapsed
    
    if remaining <= 0:
        self._stop_jail_mode()  # Auto-unlock when session ends
        self.state = FocusState.COMPLETED

def _start_jail_mode(self):
    from productivity_enforcer import ProductivityEnforcer
    self.jail_enforcer = ProductivityEnforcer()
    self.jail_enforcer.start_enforcement(duration_hours)
    # Start monitoring thread to kill blocked processes
    threading.Thread(target=self.jail_enforcer.monitor_loop, daemon=True).start()
```

**Timer Format:** `MM:SS` display, progress bar 0-100%, color coding (green → orange when <5min)

---

### 6. **productivity_enforcer.py** - Distraction Blocker (THE CORE!)
**Purpose:** Nuclear-level blocking via hosts file + process termination

**🔒 Blocking Strategy:**

1. **Hosts File Modification:**
```python
def modify_hosts_file(self, block=True):
    # Read C:\Windows\System32\drivers\etc\hosts
    with open(self.hosts_file, 'r') as f:
        lines = f.readlines()
    
    # Add blocking entries
    for site in self.blocked_sites:
        lines.append(f"127.0.0.1 {site} # PRODUCTIVITY_BLOCKER\n")
    
    # Write back (requires admin privileges!)
    with open(self.hosts_file, 'w') as f:
        f.writelines(lines)
    
    # Flush DNS cache so changes take effect immediately
    subprocess.run(["ipconfig", "/flushdns"])
```

2. **Process Termination:**
```python
def monitor_processes(self):
    for proc in psutil.process_iter(['pid', 'name']):
        proc_name = proc.info['name'].lower()
        if proc_name in self.blocked_apps:
            print(f"🚫 Blocking {proc_name}")
            proc.terminate()  # Kill the process
```

3. **Browser Content Monitoring:**
```python
def check_browser_content(self):
    # Enumerate all visible windows
    windows = []
    win32gui.EnumWindows(enum_windows_callback, windows)
    
    for window_title in windows:
        if "youtube" in window_title:
            if not self.check_youtube_content(window_title):
                self.show_block_message("YouTube content blocked")
```

**Blocked Categories (40+ items):**
- **Social Media:** Facebook, Twitter, Instagram, TikTok, Discord, Snapchat
- **Entertainment:** Reddit, YouTube (non-educational), 9gag, Buzzfeed
- **Gaming:** Steam, Epic Games, Twitch, Battle.net, Riot Games
- **News:** CNN, BBC, Hacker News
- **Shopping:** Amazon, eBay, AliExpress
- **Apps:** Discord.exe, Spotify.exe, Steam.exe, Torrent clients

**Allowed (Whitelist):**
- **Dev Tools:** VS Code, PyCharm, IntelliJ, terminals, Git
- **Educational:** NeetCode, MIT/Stanford lectures, CS50, Khan Academy, FreeCodeCamp
- **Work Sites:** GitHub, Stack Overflow, GeeksforGeeks, documentation sites

**YouTube Smart Filtering:**
```python
def check_youtube_content(self, title):
    allowed = ['neetcode', 'mit', 'stanford', 'freecodecamp', 'tutorial', 'lecture', 'course']
    blocked = ['funny', 'meme', 'react', 'prank', 'fail', 'gaming', 'music video']
    
    # Allow if matches educational keywords
    for kw in allowed:
        if kw in title.lower():
            return True
    
    # Block entertainment keywords
    for kw in blocked:
        if kw in title.lower():
            return False
    
    return False  # Block by default unless explicitly educational
```

**State Persistence:**
```python
def save_enforcement_state(self, end_time):
    state = {
        'active': True,
        'end_time': end_time.isoformat(),
        'started': datetime.now().isoformat()
    }
    with open('productivity_data/enforcement_state.json', 'w') as f:
        json.dump(state, f)
```

**Monitoring Loop:**
```python
def monitor_loop(self):
    while self.enforcement_active:
        # Check if session expired
        if datetime.now() >= end_time:
            self.stop_enforcement()
            break
        
        self.monitor_processes()       # Kill blocked apps every 5s
        self.check_browser_content()   # Check browser windows
        time.sleep(5)
```

**⚠️ Requires Admin Privileges:** Uses `ctypes.windll.shell32.IsUserAnAdmin()` to check

---

### 7. **dashboard.py** - 3-Tab Tkinter GUI
**Purpose:** Main user interface with real-time updates

**Tab 1: Focus**
- Mode selection (Pomodoro vs Deep Work)
- Start/Stop buttons
- Timer display (MM:SS format, 36pt bold font)
- Progress bar
- Jail status indicator
- Manual jail controls (2h/4h/8h buttons)
- Current activity display

**Tab 2: Activities**
- Editable treeview with columns: start, end, label, category, duration
- Double-click cells to edit
- Add/Delete/Save buttons
- Auto-refreshes with logged sessions
- Avoids refresh during editing (prevents item-not-found errors)

**Tab 3: Statistics**
- Range selector: Today / This Week / This Month / This Year
- Daily: Category breakdown with horizontal bars
- Weekly: 7-day bar chart with per-day hours
- Monthly: Category totals for the month
- Yearly: Quarterly summaries (Q1-Q4)

**Refresh Loop (2-second interval):**
```python
def _start_refresh_loop(self):
    self._update_focus()      # Timer countdown
    self._update_activity()   # Current app display
    self._update_stats()      # Stats tab data
    self.root.after(2000, self._start_refresh_loop)
```

**Color Coding:**
```python
'Building': '#4CAF50'   # Green (coding)
'Studying': '#2196F3'   # Blue (learning)
'Applying': '#FF9800'   # Orange (job search)
'Knowledge': '#9C27B0'  # Purple (research)
```

---

### 8. **stats_calculator.py** - Analytics Engine
**Purpose:** Aggregates data for weekly/monthly/yearly insights

**Key Calculations:**

**Weekly Stats:**
```python
def calculate_weekly_stats(self, start_date=None):
    weekly_data = self.data_logger.get_weekly_data(start_date)
    
    # Aggregate 7 days
    weekly_totals = {'building': 0, 'studying': 0, ...}
    for day in weekly_data:
        for category in weekly_totals:
            weekly_totals[category] += day['daily_summary'][category]
    
    # Find best day
    best_day = max(daily_summaries, key=lambda x: x['total'])
    
    # Calculate consistency (% of days with >2h work)
    consistency = len([d for d in weekly_data if d['total_productive'] > 120]) / 7
    
    return {
        'totals': weekly_totals,
        'best_day': best_day,
        'average_daily': weekly_totals['total_productive'] / 7,
        'consistency': consistency
    }
```

**Monthly Stats:**
- Group days into weeks
- Find best week
- Count days with meaningful work (>2h)

**Yearly Stats:**
- Aggregate into quarters (Q1-Q4)
- Monthly totals array [Jan, Feb, ..., Dec]
- Best month/quarter identification

---

### 9. **trend_analyzer.py** - Growth Tracking
**Purpose:** Detects productivity patterns and generates insights

**Weekly Trends (4-week comparison):**
```python
def analyze_weekly_trends(self, weeks_back=4):
    trends = []
    for i in range(weeks_back):
        week_stats = calculate_weekly_stats(week_start)
        trends.append({'total_hours': ..., 'consistency': ...})
    
    # Calculate growth percentage
    growth = ((latest['total_hours'] - previous['total_hours']) / previous['total_hours']) * 100
    
    return {
        'growth_percentage': growth,
        'trend_direction': 'up' if growth > 0 else 'down',
        'most_improved_category': find_most_improved_category(trends)
    }
```

**Insights Generation:**
```python
def get_productivity_insights(self):
    insights = []
    
    if growth_percentage > 10:
        insights.append(f"📈 Great progress! Up {growth}% from last week")
    
    if category_improvement > 20:
        insights.append(f"🚀 {category} time up {improvement}%!")
    
    if consistency_trend == 'improving':
        insights.append("⭐ Your consistency is improving month over month")
    
    return insights[:3]  # Top 3 insights
```

**Monthly Prediction:**
```python
def predict_monthly_total(self):
    days_elapsed = datetime.now().day
    days_remaining = days_in_month - days_elapsed
    daily_average = current_total / days_elapsed
    predicted_total = current_total + (daily_average * days_remaining)
```

---

## 🔥 Key Technical Decisions & Why

### 1. **Why Win32 APIs instead of just psutil?**
- `psutil.process_iter()` gives process names, but not **active window**
- Need `win32gui.GetForegroundWindow()` to know what user is currently focused on
- Window title provides richer context (e.g., "main.py - VS Code" vs just "code.exe")

### 2. **Why hosts file instead of browser extensions?**
- **System-level blocking** → works across all browsers (Chrome, Firefox, Edge)
- **Cannot be disabled easily** → user would need admin access to unblock
- **Works for desktop apps too** → blocks Discord.exe, Steam.exe, not just websites
- Downside: Requires admin privileges, Windows-specific

### 3. **Why JSON files instead of SQLite?**
- **Simplicity:** One file per day, easy to inspect/debug
- **Portability:** Can zip and share data easily
- **No dependencies:** Standard library only
- **Human-readable:** Can manually edit if needed
- Downside: Slower for complex queries (but dataset is small)

### 4. **Why Tkinter instead of web-based (Flask/React)?**
- **Zero setup:** No localhost servers, just `python main.py`
- **Native Windows integration:** Can modify hosts file, kill processes
- **Lower resource usage:** Single Python process, no browser overhead
- **Offline-first:** No internet required
- Downside: Less modern UI, harder to style

### 5. **Why 1-second polling instead of event-driven?**
- **Win32 window hooks are complex** → need low-level keyboard/mouse hooks
- **Event-driven = more code** → harder to debug
- **1-second latency is acceptable** → user doesn't notice
- **Simpler architecture:** Just `while True: poll(); sleep(1)`

### 6. **Why daemon threads?**
- **Clean shutdown:** When main thread exits, daemon threads auto-terminate
- **No zombie processes:** Prevents orphaned monitoring threads
- Downside: Won't complete ongoing operations on shutdown (but that's acceptable here)

---

## 📊 Key Metrics & Performance

### Scale:
- **2,718 lines of code** (Python)
- **50+ applications tracked** (VS Code, Chrome, Discord, Steam, etc.)
- **40+ blocked sites/apps** during focus mode
- **1,000+ activity events per session** (based on README)
- **7 major modules** (activity monitor, enforcer, dashboard, etc.)

### Performance:
- **1-second polling rate** for activity monitoring
- **5-second polling rate** for process blocking (during jail mode)
- **2-second refresh rate** for GUI updates
- **5-minute idle timeout** before pausing tracking
- **30-second minimum session length** (filters noise)

### Storage:
- **~50KB per day** of JSON data (depends on session count)
- **Daily data files** (one per day, YYYY-MM-DD.json format)
- **Persistent state** for enforcement across app restarts

---

## 🚀 Cool Features to Highlight

### 1. **Pseudo-Productive Detection** (Unique!)
Most productivity trackers just log time. Foco **detects fake work:**
- Watching programming tutorials on YouTube = flagged
- LinkedIn feed scrolling = flagged
- Reddit "research" = flagged

### 2. **Smart YouTube Filtering**
Allows NeetCode, MIT lectures, FreeCodeCamp → blocks funny videos, music, vlogs
Uses keyword scoring: educational_keywords vs blocked_keywords

### 3. **Automatic Jail Mode**
Deep Work (90 min) sessions **automatically enable blocking** → you can't disable it early
Forces focus by removing escape routes

### 4. **Context Switch Tracking**
Counts how many times you switched apps → high switches = distracted day
Helps identify focus issues

### 5. **Trend Analysis**
Not just "what did I do today?" → "Am I improving week-over-week?"
Growth percentage, consistency scores, category improvements

### 6. **Manual Override**
Can manually start 2h/4h/8h jail mode without a focus session
Useful for "I just need to lock myself down NOW"

---

## 🎤 Interview Talking Points

### What makes this interesting?
1. **Real-world problem solving:** Built for personal ADHD struggles, actual users at UF
2. **System-level control:** Not just a timer app, modifies OS files (hosts) and kills processes
3. **Smart categorization:** Not just time tracking, understands context (pseudo-productive detection)
4. **User psychology:** Designed around cognitive struggles (automatic jail, can't cheat)

### Technical challenges solved:
1. **Admin privilege handling:** Needed to modify hosts file, required ctypes checks
2. **Thread safety:** GUI on main thread, monitoring on background thread → careful with shared state
3. **Real-time window tracking:** Win32 APIs are complex, needed to poll PID → process → window title
4. **Hosts file race conditions:** Backup before modify, restore on crash
5. **Cross-process termination:** psutil access denied errors, needed proper exception handling

### What would you improve? (Self-reflection)
1. **Database instead of JSON:** Scale to 1+ year of data, faster queries
2. **Machine learning categorization:** Instead of keyword matching, train a model on labeled data
3. **Cross-platform support:** Currently Windows-only, would need macOS/Linux equivalents
4. **Web dashboard:** Modern React UI instead of Tkinter
5. **Browser extensions:** More granular control over what's blocked (specific subreddits vs all of Reddit)
6. **Notification system:** Alert before session ends, remind to take breaks
7. **Team features:** Compare stats with peers, accountability partners

### Scale considerations:
- Currently single-user, single-machine
- To scale: Need cloud sync, multi-device support, user accounts
- Database would be essential (PostgreSQL or MongoDB)
- Would need API layer (FastAPI or Flask)

---

## 📝 Code Examples for Interview

### Example 1: Window Tracking
**Question:** "How do you track which application the user is using?"

```python
import win32gui
import win32process
import psutil

def get_active_window_info():
    # Get handle of the currently active (foreground) window
    hwnd = win32gui.GetForegroundWindow()
    
    # Extract window title (e.g., "main.py - Visual Studio Code")
    window_title = win32gui.GetWindowText(hwnd)
    
    # Get the process ID associated with this window
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    
    # Use psutil to get process details
    process = psutil.Process(pid)
    process_name = process.name()  # e.g., "code.exe"
    
    return process_name, window_title

# Called every 1 second in background thread
while True:
    app, title = get_active_window_info()
    print(f"Active: {app} - {title}")
    time.sleep(1)
```

### Example 2: Smart Categorization
**Question:** "How do you categorize activities?"

```python
def categorize_activity(app_name, window_title):
    app_lower = app_name.lower()
    title_lower = window_title.lower()
    
    # Building (coding)
    if any(ide in app_lower for ide in ['code.exe', 'pycharm', 'idea64']):
        return 'Building'
    
    # Studying (learning)
    if any(keyword in title_lower for keyword in ['canvas', 'coursera', 'udemy']):
        return 'Studying'
    
    # Applying (job search)
    if 'linkedin' in title_lower and any(kw in title_lower for kw in ['job', 'apply']):
        return 'Applying'
    
    # Default to Knowledge
    return 'Knowledge'

def is_pseudo_productive(app_name, window_title):
    title_lower = window_title.lower()
    
    # YouTube programming videos = watching, not doing
    if 'youtube' in title_lower:
        if any(kw in title_lower for kw in ['programming', 'tutorial', 'coding']):
            return True
    
    # Social media = always pseudo-productive
    if any(site in title_lower for site in ['reddit', 'twitter', 'facebook']):
        return True
    
    return False
```

### Example 3: Hosts File Blocking
**Question:** "How do you block websites?"

```python
import subprocess

def modify_hosts_file(blocked_sites, block=True):
    hosts_file = r"C:\Windows\System32\drivers\etc\hosts"
    
    # Read current file
    with open(hosts_file, 'r') as f:
        lines = f.readlines()
    
    # Remove old blocking entries
    lines = [line for line in lines if not line.strip().endswith("# PRODUCTIVITY_BLOCKER")]
    
    if block:
        # Add new blocking entries
        lines.append("\n# PRODUCTIVITY BLOCKER\n")
        for site in blocked_sites:
            lines.append(f"127.0.0.1 {site} # PRODUCTIVITY_BLOCKER\n")
    
    # Write back (requires admin!)
    with open(hosts_file, 'w') as f:
        f.writelines(lines)
    
    # Flush DNS so changes take effect immediately
    subprocess.run(["ipconfig", "/flushdns"], capture_output=True)

# Block list
blocked = ["reddit.com", "www.reddit.com", "twitter.com", "youtube.com"]
modify_hosts_file(blocked, block=True)
```

### Example 4: Focus Timer with Auto-Jail
**Question:** "How does the focus session work?"

```python
from datetime import datetime, timedelta
import threading

class FocusManager:
    def __init__(self):
        self.start_time = None
        self.mode = None  # 'deep' (90 min) or 'quick' (25 min)
        self.durations = {'deep': 90, 'quick': 25}
    
    def start_session(self, mode):
        self.mode = mode
        self.start_time = datetime.now()
        
        # Auto-enable jail mode for Deep Work
        if mode == 'deep':
            self.start_jail_mode()
    
    def get_remaining_time(self):
        if not self.start_time:
            return 0
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        target = self.durations[self.mode] * 60  # Convert to seconds
        remaining = max(0, target - elapsed)
        
        return remaining
    
    def update(self):
        remaining = self.get_remaining_time()
        
        if remaining == 0:
            self.stop_jail_mode()  # Auto-unlock when done
            print("Session complete!")
        
        # Format as MM:SS
        minutes = int(remaining // 60)
        seconds = int(remaining % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def start_jail_mode(self):
        from productivity_enforcer import ProductivityEnforcer
        self.enforcer = ProductivityEnforcer()
        self.enforcer.start_enforcement(self.durations[self.mode] / 60)
        
        # Start monitoring in background
        threading.Thread(target=self.enforcer.monitor_loop, daemon=True).start()
```

### Example 5: Process Termination
**Question:** "How do you block applications?"

```python
import psutil

def block_processes(blocked_apps):
    """Kill any processes that match blocked apps list"""
    
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            proc_name = proc.info['name'].lower()
            
            # Check if this process should be blocked
            if proc_name in [app.lower() for app in blocked_apps]:
                print(f"🚫 Terminating {proc_name} (PID: {proc.info['pid']})")
                proc.terminate()  # Gracefully terminate
                
                # If it doesn't die, force kill
                try:
                    proc.wait(timeout=3)  # Wait up to 3 seconds
                except psutil.TimeoutExpired:
                    proc.kill()  # Force kill
                    
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass  # Process already gone or no permission

# Monitoring loop (runs every 5 seconds)
blocked_apps = ['steam.exe', 'discord.exe', 'spotify.exe']
while True:
    block_processes(blocked_apps)
    time.sleep(5)
```

### Example 6: Data Persistence
**Question:** "How do you store data?"

```python
import json
from datetime import datetime

class DataLogger:
    def __init__(self):
        self.data_dir = "productivity_data"
        self.today_data = self.load_today_data()
    
    def get_today_filename(self):
        today = datetime.now().strftime('%Y-%m-%d')
        return f"{self.data_dir}/{today}.json"
    
    def end_session(self, session_data):
        # Add to sessions list
        self.today_data["sessions"].append(session_data)
        
        # Update daily summary
        category = session_data['category'].lower()
        duration = session_data['duration_minutes']
        
        if session_data['is_pseudo_productive']:
            self.today_data["daily_summary"]["pseudo_productive"] += duration
        else:
            self.today_data["daily_summary"][category] += duration
            self.today_data["daily_summary"]["total_productive"] += duration
        
        # Save to file
        with open(self.get_today_filename(), 'w') as f:
            json.dump(self.today_data, f, indent=2)

# Example usage
logger = DataLogger()
logger.end_session({
    'start_time': '14:30',
    'end_time': '15:00',
    'application': 'code.exe',
    'category': 'Building',
    'duration_minutes': 30,
    'is_pseudo_productive': False
})
```

---

## 🎯 Quick Facts for Citadel Interview

### Numbers to Remember:
- **2,718** lines of code
- **50+** applications tracked
- **40+** blocked sites/apps
- **1,000+** activity events logged per session
- **7** major modules
- **4** activity categories (Building/Studying/Applying/Knowledge)
- **2** focus modes (25 min Pomodoro, 90 min Deep Work)
- **1 second** polling rate for activity
- **5 seconds** polling rate for enforcement
- **5 minutes** idle timeout

### Tech Stack:
- **Python** (core language)
- **Tkinter** (GUI framework)
- **Win32 APIs** (window tracking: win32gui, win32process)
- **psutil** (process monitoring)
- **JSON** (data persistence)
- **threading** (background monitoring)
- **matplotlib** (analytics visualization)

### Key Libraries:
```python
import tkinter as tk           # GUI
import psutil                  # Process monitoring
import win32gui                # Window tracking
import win32process            # Process info
from datetime import datetime  # Time tracking
import json                    # Data storage
import threading               # Background tasks
```

### Architecture Pattern:
- **MVC-ish:** Dashboard (View), Data Logger (Model), Activity Monitor (Controller)
- **Event-driven:** Background thread polls → triggers updates → GUI refreshes
- **Modular:** Each module has single responsibility (SRP)

### Unique Features:
1. **Pseudo-productive detection** (catches "fake work")
2. **Smart YouTube filtering** (educational only)
3. **Automatic jail mode** (can't escape Deep Work sessions)
4. **System-level blocking** (hosts file + process termination)
5. **Context switch tracking** (identifies distraction patterns)

### Real-World Impact:
- Used by peers at **University of Florida**
- Tracked **1,000+ events per session**
- Helps **ADHD students** stay focused
- **Personal project** → solved own productivity struggles

---

## 🎤 How to Present This in Interview

### 30-Second Pitch:
> "I built **Foco**, a Windows productivity tracker for ADHD students. It uses **Win32 APIs** to monitor 50+ apps in real-time, **categorizes activities** into Building/Studying/Applying/Knowledge, and has a unique **pseudo-productive detection** system that flags when you're watching programming tutorials instead of actually coding. The killer feature is **jail mode** – during 90-minute Deep Work sessions, it automatically blocks 40+ distracting sites via hosts file modification and terminates processes like Discord and Steam. It's been used by peers at UF and has tracked over 1,000+ activity events per session. Built in **Python** with **Tkinter**, **psutil**, and **Win32 APIs**. 2,700 lines of code."

### If Asked About Technical Challenges:
> "The hardest part was real-time window tracking. You can't just use `psutil` – it gives you processes but not which window is active. I needed `win32gui.GetForegroundWindow()` to get the active window handle, then `win32process.GetWindowThreadProcessId()` to map that to a process, then finally `psutil.Process()` to get the name. All in a background thread that polls every second without blocking the GUI. Also, modifying the hosts file requires admin privileges, so I had to handle `ctypes.windll.shell32.IsUserAnAdmin()` checks and gracefully degrade if not running elevated."

### If Asked What You'd Improve:
> "If I were to scale this, I'd replace JSON files with **PostgreSQL** for better query performance, add a **React web dashboard** for modern UI, build **browser extensions** for more granular control (like blocking specific subreddits), and use **machine learning** for categorization instead of keyword matching. I'd also add **cloud sync** for multi-device support and **team features** like comparing stats with accountability partners."

---

## 🏁 Final Summary

**Foco** is a **2,718-line Python desktop app** that helps ADHD students stay focused by:
1. **Monitoring** 50+ apps using Win32 APIs (1-second polling)
2. **Categorizing** work into 4 categories with pseudo-productive detection
3. **Blocking** 40+ distracting sites/apps via hosts file + process termination
4. **Tracking** productivity with daily/weekly/monthly/yearly analytics
5. **Enforcing** focus with Pomodoro (25 min) and Deep Work (90 min) modes

**Key Innovation:** Detects fake work (watching tutorials ≠ coding), auto-enables jail mode for Deep Work, allows only educational YouTube content.

**Tech Stack:** Python, Tkinter, Win32 APIs, psutil, JSON, threading.

**Impact:** Used by UF students, tracked 1,000+ events per session.

---

**Good luck with your Citadel interview! 🚀**

You've got this – you built a real system that solves a real problem, uses low-level OS APIs, handles concurrency, and has actual users. That's more than most candidates can say!
