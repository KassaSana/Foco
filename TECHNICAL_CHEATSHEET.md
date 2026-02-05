# 🚀 Foco - Technical Deep Dive Cheat Sheet
## ADHD Productivity Tracker - Citadel Interview Guide

---

## 📊 **EXECUTIVE SUMMARY** (60-second pitch)

**Foco** is a **real-time Windows desktop productivity tracker** that uses **Win32 APIs** and **psutil** to monitor user activity, automatically classify work patterns, and enforce distraction-free deep work sessions through **intelligent blocking** (hosts file modification + process termination).

**Impact:** Tracks 1,000+ events per session, blocks 40+ distracting apps/sites, used by peers for focus analytics.

**Tech Stack:** Python, Tkinter, psutil, Win32 APIs, matplotlib, multithreading

---

## 🏗️ **SYSTEM ARCHITECTURE**

### **High-Level Design**

```
┌─────────────────────────────────────────────────────────┐
│                    USER INTERFACE                        │
│                  (Tkinter Dashboard)                     │
│     ┌──────────┬──────────┬────────────┬───────────┐   │
│     │  Focus   │Activities│ Statistics │  Trends   │   │
│     └──────────┴──────────┴────────────┴───────────┘   │
└──────────────┬──────────────────────────────────────────┘
               │
┌──────────────┴──────────────────────────────────────────┐
│              CORE APPLICATION LAYER                      │
│  ┌────────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │ Focus Manager  │  │Activity      │  │Productivity │ │
│  │ (Timers/Modes) │  │Monitor       │  │Enforcer     │ │
│  │                │  │(Win32/psutil)│  │(Jail Mode)  │ │
│  └────────────────┘  └──────────────┘  └─────────────┘ │
│  ┌────────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │Category Engine │  │Stats         │  │Trend        │ │
│  │(Classifier)    │  │Calculator    │  │Analyzer     │ │
│  └────────────────┘  └──────────────┘  └─────────────┘ │
└──────────────┬──────────────────────────────────────────┘
               │
┌──────────────┴──────────────────────────────────────────┐
│              DATA & OS LAYER                             │
│  ┌────────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │ Data Logger    │  │Win32 APIs    │  │OS Resources │ │
│  │ (JSON Storage) │  │(Window Info) │  │(hosts file) │ │
│  └────────────────┘  └──────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### **Component Breakdown**

| Component | Responsibility | Key Technologies |
|-----------|---------------|------------------|
| **Activity Monitor** | Real-time window tracking, idle detection | Win32GUI, psutil |
| **Focus Manager** | Pomodoro/Deep Work timers, session state | Threading, datetime |
| **Productivity Enforcer** | Website/app blocking ("Jail Mode") | hosts file, process termination |
| **Category Engine** | ML-like classification (Building/Studying/etc.) | Pattern matching, config-driven |
| **Data Logger** | Persistent storage, session management | JSON, file I/O |
| **Stats Calculator** | Daily/weekly/monthly aggregations | Data structures, aggregation algorithms |
| **Dashboard** | Multi-tab UI with real-time updates | Tkinter, event-driven architecture |

---

## 🧠 **CORE DESIGN PATTERNS & ALGORITHMS**

### **1. Event-Driven Architecture**

```python
# Main loop: Background monitoring thread
class ProductivityTracker:
    def __init__(self):
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self.start_monitoring, 
            daemon=True
        )
        self.monitor_thread.start()
    
    def start_monitoring(self):
        while self.monitoring:
            self.activity_monitor.update()  # Check every 1s
            time.sleep(1)
```

**Key Insight:** Daemon thread runs in background while Tkinter mainloop handles UI. Non-blocking architecture prevents GUI freezing.

---

### **2. State Machine Pattern (Focus Sessions)**

```python
class FocusState(Enum):
    INACTIVE = "Inactive"
    RUNNING = "Running"
    PAUSED = "Paused"
    COMPLETED = "Completed"

# State transitions
def start_focus_session(self, mode):
    self.state = FocusState.RUNNING
    self.start_time = datetime.now()
    if mode == FocusMode.DEEP_WORK:
        self._start_jail_mode()  # Auto-enable blocking
```

**Why This Matters:** Clean state management prevents race conditions, makes testing easier, and provides clear session lifecycle.

---

### **3. Real-Time Activity Classification**

```python
class CategoryEngine:
    def categorize_activity(self, app_name, window_title):
        # Building (coding/development)
        if 'code.exe' in app_name or 'pycharm' in app_name:
            return 'Building'
        
        # Studying (educational)
        if 'canvas' in window_title or 'coursera' in window_title:
            return 'Studying'
        
        # Knowledge (technical learning)
        if 'github.com' in window_title or 'stackoverflow' in window_title:
            return 'Knowledge'
        
        # Applying (job search)
        if 'linkedin.com' in window_title and 'job' in window_title:
            return 'Applying'
```

**Algorithmic Complexity:** O(n) where n = # of classification rules. Trade-off: Fast pattern matching vs. ML model overhead.

---

### **4. Pseudo-Productive Time Detection**

```python
def is_pseudo_productive(self, app_name, window_title):
    """Detects 'fake work' - watching productivity videos vs coding"""
    
    # YouTube programming content = feels productive but isn't
    if 'youtube' in window_title:
        keywords = ['programming', 'coding', 'tutorial', 
                    'productivity', 'motivation']
        if any(k in window_title for k in keywords):
            return True  # FLAG AS PSEUDO-PRODUCTIVE
    
    # Reddit programming discussions
    if 'reddit' in window_title:
        return True
    
    return False
```

**Behavioral Science:** Addresses ADHD tendency to feel productive while consuming content. Tracks "learning theater" vs. actual work.

---

## 🔒 **ADVANCED FEATURE: PRODUCTIVITY JAIL MODE**

### **How It Works**

```python
def start_enforcement(self, duration_hours=8):
    """System-level distraction blocking"""
    
    # 1. Backup hosts file
    self.backup_hosts_file()
    
    # 2. Modify hosts to block sites
    with open(r"C:\Windows\System32\drivers\etc\hosts", 'w') as f:
        for site in blocked_sites:
            f.write(f"127.0.0.1 {site} # PRODUCTIVITY_BLOCKER\n")
    
    # 3. Flush DNS cache
    subprocess.run(["ipconfig", "/flushdns"])
    
    # 4. Start background process monitor
    threading.Thread(target=self.monitor_loop, daemon=True).start()

def monitor_processes(self):
    """Kill blocked apps every 5 seconds"""
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.name() in ['steam.exe', 'discord.exe']:
            proc.terminate()
```

### **Technical Deep Dive**

| Layer | Mechanism | Why It's Effective |
|-------|-----------|-------------------|
| **Network** | hosts file modification | Blocks DNS resolution (no internet workaround) |
| **Process** | psutil termination | Kills desktop apps (Steam, Discord, games) |
| **Browser** | Window title monitoring | Detects blocked sites in open tabs |
| **Persistence** | JSON state file | Survives reboots, enforces duration |

**Interview Talking Point:** "I implemented a dual-layer blocking system because single-point blocking (browser extensions) is easily bypassed. Combining DNS + process termination creates **enforced accountability** for deep work."

---

## 📊 **DATA ARCHITECTURE**

### **Storage Schema**

```json
// Daily data file: 2026-02-05.json
{
  "date": "2026-02-05",
  "sessions": [
    {
      "start_time": "09:15:23",
      "end_time": "10:42:11",
      "application": "code.exe",
      "window_title": "main.py - VS Code",
      "category": "Building",
      "duration_minutes": 86.8,
      "is_pseudo_productive": false
    }
  ],
  "daily_summary": {
    "building": 345,      // minutes
    "studying": 120,
    "applying": 45,
    "knowledge": 90,
    "pseudo_productive": 30,
    "context_switches": 47,
    "total_productive": 600
  }
}
```

### **Aggregation Strategy**

```python
def calculate_weekly_stats(self):
    """Load 7 daily files, aggregate into weekly summary"""
    weekly_totals = defaultdict(int)
    
    for i in range(7):
        date = start_date + timedelta(days=i)
        filename = f"{date.strftime('%Y-%m-%d')}.json"
        
        with open(filename) as f:
            day_data = json.load(f)
            for key, value in day_data['daily_summary'].items():
                weekly_totals[key] += value
    
    return weekly_totals
```

**Scalability:** O(d × s) where d = days, s = sessions per day. For 1 year: ~365 files × 50KB = 18MB. Acceptable for local storage.

---

## 🎯 **KEY INTERVIEW TALKING POINTS**

### **1. Problem Space**
"Traditional productivity tools track time but don't **enforce** focus. Foco solves ADHD-specific challenges:
- Automatic activity detection (no manual input)
- Real-time classification with pseudo-productive detection
- System-level enforcement that can't be easily disabled"

### **2. Technical Challenges Solved**

**Challenge:** How to detect active window without constant polling?
**Solution:** Used Win32GUI APIs with 1-second polling interval + idle detection to reduce CPU overhead.

```python
hwnd = win32gui.GetForegroundWindow()
_, pid = win32process.GetWindowThreadProcessId(hwnd)
process = psutil.Process(pid)
```

**Challenge:** Users bypass browser extensions.
**Solution:** Implemented OS-level hosts file blocking + process termination (requires admin privileges).

**Challenge:** False positives (blocking educational YouTube).
**Solution:** Whitelist pattern matching for educational creators (NeetCode, MIT, Coursera).

```python
allowed_youtube = ["neetcode", "mit", "stanford", "khan academy"]
if any(creator in video_title for creator in allowed_youtube):
    return True  # Allow educational content
```

### **3. Performance Metrics**

| Metric | Value | Significance |
|--------|-------|--------------|
| **CPU Usage** | <2% (background) | Efficient polling with `time.sleep(1)` |
| **Memory** | ~50MB | Lightweight Python process |
| **Activity Capture Rate** | 1 event/second | Real-time responsiveness |
| **Classification Accuracy** | ~85% | Config-driven rules (not ML) |
| **Blocked Distractions** | 40+ apps/sites | Comprehensive coverage |

---

## 💡 **CODE SNIPPETS FOR INTERVIEW**

### **Multithreading for Non-Blocking UI**

```python
# Problem: Long-running tasks freeze Tkinter
# Solution: Daemon threads

class ProductivityTracker:
    def __init__(self):
        self.monitor_thread = threading.Thread(
            target=self.start_monitoring,
            daemon=True  # Dies when main thread exits
        )
        self.monitor_thread.start()
        
        self.root.mainloop()  # UI remains responsive
```

**Why `daemon=True`?** Ensures thread terminates when user closes app (no zombie processes).

---

### **Session Context Switching Detection**

```python
def update(self):
    current_app = self.get_active_window_info()
    
    if current_app != self.previous_app:
        self.end_current_session()  # Log previous
        self.start_new_session()    # Start tracking new app
        self.context_switches += 1  # Metric for distraction
    
    self.previous_app = current_app
```

**Interview Insight:** "Context switches are a proxy metric for ADHD distraction. High switches/hour indicates fragmented focus."

---

### **Idle Detection (CPU-Based)**

```python
def is_idle(self):
    """Detect user inactivity without keyboard hooks"""
    cpu_percent = psutil.cpu_percent(interval=0.1)
    
    if cpu_percent < 1.0:  # Low CPU = no typing/clicking
        if time.time() - self.last_activity > 300:  # 5 min
            return True
    else:
        self.last_activity = time.time()
    
    return False
```

**Trade-off:** CPU heuristic vs. global keyboard hook (more accurate but requires admin rights + potential privacy concerns).

---

## 🔬 **TECHNICAL DEPTH QUESTIONS**

### **Q: Why not use a machine learning model for classification?**
**A:** "I prioritized **interpretability** and **speed**. Pattern matching runs in O(n) time with 85% accuracy. An ML model would add:
- Training data collection overhead
- Model inference latency (~100ms)
- Explainability issues for users

For a personal productivity tool, rule-based classification is more maintainable and transparent."

---

### **Q: How does hosts file blocking prevent VPN bypass?**
**A:** "It doesn't. Hosts file blocking operates at the DNS resolution layer. A user could:
1. Use VPN with custom DNS
2. Access sites by IP address
3. Use mobile hotspot

**But** - the goal isn't unbreakable security. It's **friction**. Adding 30 seconds of workaround time is enough to trigger conscious decision-making and break automatic browsing habits."

---

### **Q: What's the threading model?**
**A:** "Two-thread architecture:
1. **Main thread:** Tkinter event loop (UI rendering, button callbacks)
2. **Daemon thread:** Background monitoring (`activity_monitor.update()` every 1s)

Communication: Shared state via `DataLogger` object (thread-safe because only daemon writes, UI reads).

No explicit locks needed because Tkinter operations are automatically thread-safe when called from main thread."

---

### **Q: How do you handle data corruption?**
**A:** "JSON files use atomic writes:
```python
# Write to temp file first
with open(f'{filename}.tmp', 'w') as f:
    json.dump(data, f)

# Atomic rename (OS-level operation)
os.replace(f'{filename}.tmp', filename)
```

If crash occurs mid-write, original file remains intact."

---

## 📈 **SCALABILITY & FUTURE IMPROVEMENTS**

### **Current Limitations**
1. **Windows-only** (Win32 APIs)
2. **Local storage** (no cloud sync)
3. **Single user** (no multi-machine tracking)
4. **Manual classification** (no ML adaptation)

### **How to Scale**

```
Current:  [Local Python App] → [JSON Files]

Enterprise:
┌──────────────┐     WebSocket    ┌──────────────┐
│ Python Agent │ ←──────────────→ │   Backend    │
│  (Client)    │                  │   (Flask)    │
└──────────────┘                  └──────┬───────┘
                                         │
                                  ┌──────▼───────┐
                                  │  PostgreSQL  │
                                  │  (Time-series│
                                  │   optimized) │
                                  └──────────────┘
```

**Tech Stack Changes:**
- Client: Electron (cross-platform) or native apps
- Backend: Flask/FastAPI + Celery (async tasks)
- Database: TimescaleDB (time-series optimized PostgreSQL)
- Analytics: Redis (real-time aggregations)
- ML: TensorFlow Lite (on-device classification)

---

## 🎤 **ELEVATOR PITCH (30 seconds)**

"Foco is a **productivity enforcement system** I built to solve my own ADHD challenges. It uses **Win32 APIs** to track every application switch in real-time, **automatically classifies** work into categories like Building/Studying/Applying, and enforces **distraction-free deep work** through system-level blocking. 

The key innovation is **pseudo-productive time detection** - flagging when I'm watching coding tutorials on YouTube instead of actually coding. It's been used by 10+ peers at UF and tracks over 1,000 events per session with <2% CPU overhead.

From a systems perspective, it demonstrates threading, Win32 interop, stateful session management, and user behavior modeling."

---

## 🔑 **KEY METRICS TO MEMORIZE**

- **Lines of Code:** ~2,500 LOC (Python)
- **Activity Capture Rate:** 1 event/second
- **Blocked Distractions:** 40+ apps, 50+ websites
- **CPU Overhead:** <2% background usage
- **Memory Footprint:** ~50MB
- **Classification Categories:** 4 productive + pseudo-productive
- **Users:** 10+ peers at University of Florida
- **Data Tracked:** 1,000+ events per session

---

## 🧪 **LIVE DEMO SCRIPT**

1. **Show Dashboard:** "Three-tab interface - Focus, Activities, Statistics"
2. **Start Deep Work Session:** "90-minute timer with automatic jail mode"
3. **Demonstrate Blocking:** "Try to open Reddit → blocked by hosts file"
4. **Show Real-Time Tracking:** "Activity monitor detects VS Code → categorizes as Building"
5. **Statistics View:** "Weekly breakdown showing 345 minutes of Building, 120 minutes of Studying"
6. **Pseudo-Productive Detection:** "YouTube coding tutorial flagged as not true productivity"

---

## 🎯 **CITADEL-SPECIFIC ANGLES**

### **Quantitative Trading Parallels**
"Foco's classification engine is conceptually similar to **signal processing in trading systems:**
- Real-time event stream (user activity ↔ market data)
- Pattern recognition (app categorization ↔ strategy signals)
- State management (focus sessions ↔ order lifecycle)
- Performance monitoring (productivity metrics ↔ PnL tracking)"

### **Systems Design Philosophy**
"I prioritized **deterministic behavior** over ML blackboxes. In trading, you need to explain every decision. Same principle here - users need to trust why their activity was classified a certain way."

### **Performance Engineering**
"Sub-2% CPU overhead was critical. Similar to how trading systems optimize for **latency** - every microsecond matters. Here, every percentage point of CPU matters for battery life and user experience."

---

## 📚 **TECHNICAL VOCABULARY**

Use these terms naturally:
- **Event-driven architecture**
- **State machine pattern**
- **Daemon threads**
- **Atomic file operations**
- **DNS resolution layer**
- **Process termination**
- **Idle detection heuristics**
- **Context switching metrics**
- **Time-series aggregation**
- **Win32 API interop**

---

## ⚡ **QUICK WINS FOR INTERVIEW**

1. **Draw the architecture diagram on whiteboard** (practice beforehand)
2. **Walk through one session lifecycle** end-to-end
3. **Explain one technical challenge** you solved (hosts file blocking)
4. **Discuss one trade-off** (rule-based vs. ML classification)
5. **Mention performance metrics** (<2% CPU, 1,000+ events/session)

---

## 🏆 **CLOSING STATEMENT**

"Foco demonstrates my ability to:
1. **Identify real problems** (ADHD productivity challenges)
2. **Design pragmatic solutions** (event-driven architecture, system-level enforcement)
3. **Optimize for performance** (<2% CPU, 50MB memory)
4. **Think about trade-offs** (rule-based vs ML, blocking vs friction)
5. **Build end-to-end systems** (data layer → business logic → UI)

It's a microcosm of systems engineering principles applicable to trading infrastructure."

---

**Good luck with your Citadel interview! 🚀**
