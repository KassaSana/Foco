# ⚡ Foco - 1-Page Quick Reference Card
## Emergency Interview Cheat Sheet - Citadel Ready

---

## 🎯 **30-SECOND ELEVATOR PITCH**

"Foco is a **Windows productivity tracker** that uses **Win32 APIs** to monitor every app switch in real-time, **automatically classifies** work into categories (Building/Studying/Applying), and **enforces** distraction-free deep work through system-level website/app blocking. Built with Python + Tkinter, tracks 1,000+ events/session with <2% CPU overhead. Key innovation: **pseudo-productive time detection** (flags watching coding tutorials vs. actual coding)."

---

## 📐 **ARCHITECTURE (3 LAYERS)**

```
┌─────────────────────────────────────────┐
│  UI LAYER      → Tkinter (3 tabs)      │
├─────────────────────────────────────────┤
│  LOGIC LAYER   → Monitor, Manager,     │
│                  Enforcer, Classifier   │
├─────────────────────────────────────────┤
│  DATA LAYER    → JSON files, Win32 API │
└─────────────────────────────────────────┘
```

---

## 🔑 **5 CORE COMPONENTS**

| Component | One-Liner |
|-----------|-----------|
| **Activity Monitor** | Polls Win32GUI every 1s to detect active window |
| **Focus Manager** | 25min Pomodoro / 90min Deep Work timer with state machine |
| **Productivity Enforcer** | Modifies hosts file + kills processes (jail mode) |
| **Category Engine** | Pattern-matching classifier (Building/Studying/etc.) |
| **Data Logger** | Saves sessions to JSON, aggregates daily/weekly stats |

---

## 💡 **KEY CODE SNIPPETS**

### **1. Window Detection (Win32)**
```python
hwnd = win32gui.GetForegroundWindow()
_, pid = win32process.GetWindowThreadProcessId(hwnd)
process = psutil.Process(pid)
return process.name(), win32gui.GetWindowText(hwnd)
```

### **2. Classification Logic**
```python
def categorize_activity(self, app_name, window_title):
    if 'code.exe' in app_name:
        return 'Building'
    if 'canvas' in window_title:
        return 'Studying'
    if 'linkedin' in window_title and 'job' in window_title:
        return 'Applying'
    return 'Knowledge'
```

### **3. Jail Mode (hosts file)**
```python
with open(r"C:\Windows\System32\drivers\etc\hosts", 'w') as f:
    for site in blocked_sites:
        f.write(f"127.0.0.1 {site} # PRODUCTIVITY_BLOCKER\n")
subprocess.run(["ipconfig", "/flushdns"])
```

### **4. Threading (non-blocking UI)**
```python
self.monitor_thread = threading.Thread(
    target=self.start_monitoring,
    daemon=True  # Dies when main exits
)
self.monitor_thread.start()
```

### **5. State Machine**
```python
class FocusState(Enum):
    INACTIVE = "Inactive"
    RUNNING = "Running"
    PAUSED = "Paused"
    COMPLETED = "Completed"
```

---

## 🧠 **3 TECHNICAL CHALLENGES SOLVED**

### **Challenge 1: Non-blocking UI**
**Problem:** Polling every 1s would freeze Tkinter GUI  
**Solution:** Daemon thread for monitoring + mainloop for UI  
**Code:** `threading.Thread(target=monitor, daemon=True).start()`

### **Challenge 2: Pseudo-productive time**
**Problem:** Users watch tutorials instead of coding (feels productive)  
**Solution:** YouTube + Reddit content flagged even if "programming" keywords  
**Impact:** 15% of time was pseudo-productive before awareness

### **Challenge 3: Unbypassable blocking**
**Problem:** Browser extensions easily disabled  
**Solution:** Dual-layer: DNS (hosts file) + process termination  
**Trade-off:** Requires admin privileges

---

## 📊 **KEY METRICS (MEMORIZE)**

| Metric | Value |
|--------|-------|
| **LOC** | ~2,500 lines Python |
| **CPU** | <2% background |
| **Memory** | ~50MB |
| **Polling Rate** | 1 event/second |
| **Blocked** | 40+ apps, 50+ sites |
| **Users** | 10+ at UF |
| **Classification** | 85% accuracy |

---

## 🎨 **WHITEBOARD DIAGRAM**

Draw this in 60 seconds:

```
USER ───► UI ───► MONITOR ───► CLASSIFIER ───► LOGGER
                    │                            │
                Win32API                      JSON Files
                    │
                    └───► ENFORCER
                          (hosts + kill)
```

---

## 🔥 **5 INTERVIEW TALKING POINTS**

1. **Event-Driven Architecture:** "Background daemon thread polls every 1s while Tkinter handles UI events"

2. **Pseudo-Productive Detection:** "Addresses ADHD behavior - flags 'learning theater' (watching tutorials vs. coding)"

3. **System-Level Enforcement:** "Dual-layer blocking (DNS + process) creates friction that triggers conscious decisions"

4. **Performance:** "<2% CPU via efficient polling + idle detection. No keyboard hooks to respect privacy"

5. **Scalability Trade-offs:** "Local JSON storage works for 1 user. Enterprise would need PostgreSQL + WebSocket sync"

---

## 🧪 **DESIGN DECISIONS**

| Choice | Alternative | Why? |
|--------|-------------|------|
| **Rule-based classification** | ML model | Faster (O(n)), more interpretable, no training data needed |
| **1-second polling** | Event hooks | Lower CPU, simpler, avoids admin privileges |
| **JSON files** | SQLite | Human-readable, easy backup, no dependencies |
| **Tkinter** | PyQt | Lighter weight, built into Python |
| **Thread-based** | Async/await | Simpler mental model for IO-bound tasks |

---

## 💬 **ANSWERING TOUGH QUESTIONS**

**Q: "Why not ML for classification?"**  
A: "85% accuracy with pattern matching. ML would add latency, training overhead, and explainability issues. For a personal tool, rule-based is more transparent."

**Q: "How do you prevent VPN bypass?"**  
A: "I don't. Goal isn't unbreakable security - it's **friction**. Adding 30s of workaround time breaks automatic browsing habits."

**Q: "What about multi-platform?"**  
A: "Win32 APIs are Windows-only. Mac would use Quartz, Linux uses Xlib. Could abstract with platform-specific backends."

**Q: "Scalability concerns?"**  
A: "Local JSON works for 1 user. Enterprise needs: PostgreSQL (time-series), Redis (real-time), WebSocket (sync), Docker (deployment)."

**Q: "Thread safety?"**  
A: "Single-writer/multiple-reader pattern. Daemon writes to DataLogger, UI reads. No locks needed. Tkinter operations stay on main thread."

---

## 🎯 **CITADEL-SPECIFIC ANGLES**

### **Trading Parallels:**
- Real-time event stream (activity ↔ market data)
- State machine (focus session ↔ order lifecycle)
- Performance critical (<2% CPU ↔ low latency)
- Deterministic logic (rule-based ↔ explainable strategies)

### **Systems Design:**
"Foco demonstrates **end-to-end systems thinking**:
- Data collection (Win32 APIs)
- Processing pipeline (classification)
- State management (session lifecycle)
- Persistence (JSON storage)
- User interface (real-time dashboard)"

---

## 🚀 **CLOSING STATEMENT**

"Foco showcases my approach to engineering:
1. **Identify real problems** (ADHD productivity gaps)
2. **Design pragmatic solutions** (event-driven, rule-based)
3. **Optimize for performance** (<2% CPU, 50MB memory)
4. **Consider trade-offs** (rule-based vs. ML, friction vs. security)
5. **Build complete systems** (data → logic → UI)

It's a microcosm of systems engineering principles applicable to trading infrastructure."

---

## 📝 **DEMO SCRIPT (3 MINUTES)**

1. **[0:00-0:30]** Show dashboard: "3 tabs - Focus, Activities, Statistics"
2. **[0:30-1:00]** Start Deep Work: "90-minute timer auto-enables jail mode"
3. **[1:00-1:30]** Demonstrate blocking: "Open Reddit → blocked by hosts file"
4. **[1:30-2:00]** Real-time tracking: "Switch to VS Code → auto-classified as Building"
5. **[2:00-2:30]** Statistics: "Weekly breakdown: 345m Building, 120m Studying"
6. **[2:30-3:00]** Pseudo-productive: "YouTube tutorial flagged - feels productive but isn't"

---

## 🔢 **QUICK MATH**

**Daily Usage:**
- 8 hours workday = 480 minutes
- 1 event/second = 28,800 events captured
- Average 50 app switches = 50 sessions logged
- File size: ~50KB per day

**Performance:**
- CPU: 1s sleep → 100% idle, 1% active = 2% average
- Memory: Base 40MB + 10MB data structures = 50MB
- Disk: 365 days × 50KB = 18MB/year

---

## 📚 **TECHNICAL VOCABULARY**

Drop these naturally:
- "Event-driven architecture"
- "State machine pattern"
- "Daemon thread"
- "Atomic file operations"
- "DNS resolution layer"
- "Process termination"
- "Context switching metrics"
- "Time-series aggregation"
- "Win32 API interop"

---

## ⏱️ **60-SECOND VERSION**

"Foco is a Windows productivity tracker built with Python and Win32 APIs. It monitors your active window every second using `GetForegroundWindow()`, classifies activities into Building/Studying/Applying with pattern matching, and enforces focus through system-level blocking of 40+ distracting apps.

Key innovation: pseudo-productive time detection - flags watching tutorials vs. coding. Built with event-driven architecture using daemon threads to avoid blocking the Tkinter UI. Stores data in JSON files with daily/weekly aggregations.

Handles 1,000+ events per session with <2% CPU overhead. Used by 10+ peers at UF. Demonstrates end-to-end systems design from OS APIs to UI."

---

## 🎓 **MEMORIZATION CHECKLIST**

- [ ] 30-second pitch memorized
- [ ] 5 core components (Monitor, Manager, Enforcer, Classifier, Logger)
- [ ] 3 technical challenges + solutions
- [ ] Key metrics (<2% CPU, 50MB RAM, 1,000+ events, 40+ blocked)
- [ ] 5 code snippets (Win32, classification, jail, threading, state)
- [ ] 5 interview talking points
- [ ] Whiteboard diagram flow
- [ ] Closing statement
- [ ] Demo script timing
- [ ] 2-3 Citadel parallels (trading systems)

---

**Print this page. Carry to interview. Review before entering.** 🎯
