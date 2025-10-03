# 🧠 ADHD Productivity Tracker - Windows App

**A simple, no-BS productivity tracker designed specifically for ADHD brains.**

Tracks your REAL work vs pseudo-productive activities (like watching "How to be a 10x developer" videos on YouTube).

## 🚀 Quick Start (One-Click Launch)

### **Easiest Way: Double-click `run_as_admin.bat`**

That's it! The app will:

- ✅ Request admin privileges (for better tracking)
- ✅ Launch the productivity dashboard
- ✅ Start monitoring automatically

### **First Time Setup**

```bash
# Run the installer first
python install.py

# Then launch
run_as_admin.bat
```

## 📱 What It Does

- **Automatically categorizes** your activities into:

  - 🔨 **Building** (VS Code, terminals, actual coding)
  - 📚 **Studying** (PDFs, Canvas, educational content)
  - 🎯 **Applying** (LinkedIn jobs, applications, networking)
  - 🧠 **Knowledge** (Stack Overflow, documentation, learning)

- **Flags pseudo-productive activities** ⚠️:

  - YouTube programming tutorials
  - Reddit browsing (even /r/programming)
  - Social media "research"
  - Motivational content consumption

- **Focus Timers**:

  - 90-minute **Deep Work** sessions
  - 25-minute **Quick Focus** sessions
  - Real active time vs total time

- **Time Navigation**: Today/Week/Month/Year views with trends

## 🖥️ App Features

### **Runs with Admin Privileges**

- Better window and application detection
- More accurate activity monitoring
- Tracks all processes properly

### **Professional Interface**

- Clean, dark-themed GUI
- Real-time activity display
- Progress bars and statistics
- No overwhelming charts or complexity

### **Local & Private**

- All data stored locally in `productivity_data/`
- No cloud sync, no accounts, no tracking
- JSON files you can read and export

## 📂 Files Overview

| File                  | Purpose                                      |
| --------------------- | -------------------------------------------- |
| `run_as_admin.bat`    | **Main launcher** (double-click this!)       |
| `install.py`          | First-time setup and dependency installation |
| `app_launcher.py`     | Smart Python launcher with admin request     |
| `main.py`             | Core application entry point                 |
| `dashboard.py`        | GUI interface (fixed flickering!)            |
| `activity_monitor.py` | Real-time window/app tracking                |
| `category_engine.py`  | Smart activity categorization                |
| `data_logger.py`      | Local data storage                           |
| `setup_app.py`        | Creates standalone .exe file                 |

## 💻 System Requirements

- **Windows 10/11**
- **Python 3.7+**
- **Admin privileges** (requested automatically)

## 🔧 Installation Options

### Option 1: Simple Python (Recommended)

1. `python install.py` - Sets up everything
2. `run_as_admin.bat` - Launch the app

### Option 2: Standalone Executable

1. `python setup_app.py` - Creates .exe file
2. Share the .exe with friends (no Python needed!)

## 🎯 Perfect For

- **CS Students** with ADHD who struggle with focus
- **Developers** who want to track real vs "fake" productivity
- **Anyone** who watches too many programming YouTube videos
- **People** who need gentle accountability without judgment

## 🧠 ADHD-Friendly Design

- **No overwhelming features** - just the essentials
- **Visual progress feedback** - see your real work vs distractions
- **Gentle reminders** - no harsh notifications or guilt
- **Focus on consistency** over perfection
- **Simple navigation** - dropdown menus and arrow buttons

## 📊 Example Dashboard

```
🧠 ADHD Productivity Tracker        Today: Monday, Sep 30 ▼

Real Work: 6.2h    Pseudo: 47m    Sessions: 3    Switches: 12

Activity Breakdown:
├─ Building: 3.1h ████████░░ (VS Code, Terminal)
├─ Studying: 1.8h █████░░░░░ (Canvas, PDFs)
├─ Applying: 1.3h ████░░░░░░ (LinkedIn Jobs)
└─ Knowledge: 0h ░░░░░░░░░░

Current: VS Code - React Project (Building) ⏱️ 12:34

[◀ Previous] [Deep Work 90min] [Quick Focus 25min] [Next ▶]
```

## 🤝 Sharing with Friends

**Easy sharing**: Just zip the whole folder and send it!

**Or create standalone**: Run `python setup_app.py` to create a single .exe file

## 🔒 Privacy

- **100% local** - no data leaves your machine
- **No accounts** - no sign-ups or profiles
- **Open source** - you can read all the code
- **Your data** - stored in readable JSON files

## 🛠️ Troubleshooting

**"Python not found"**: Install Python from python.org

**"Module not found"**: Run `python install.py`

**"Access denied"**: Allow the admin privilege request

**Window detection not working**: Make sure admin privileges were granted

**App won't start**: Check `python app_launcher.py` for error messages

## 💡 Tips

- **Run with admin** for best window detection
- **Let it track for a day** to see your patterns
- **Use focus timers** during important work
- **Check weekly/monthly** views for trends
- **Don't stress** about perfect productivity

---

**Built for ADHD brains by someone who gets it. Simple, honest, and actually helpful.** 🧠✨
