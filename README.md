# Foco 🧠
**A Python desktop app for distraction-free deep work.**

Foco helps users maintain focus by automatically detecting and blocking distracting apps and websites during study or work sessions.  
It classifies user activity in real time, logs productivity metrics, and visualizes focus patterns across days and weeks.

---

## 🚀 Features
- 🧩 **Automatic activity classification** — tracks 50+ applications using Win32 APIs  
- 🔒 **Distraction blocker** — modifies hosts file and terminates 40+ processes (Steam, Discord, YouTube, etc.)  
- 📊 **Focus dashboard** — Tkinter UI with real-time analytics of app usage and productivity trends  
- 💾 **Persistent data storage** — local session logs and historical summaries  

---

## 🧠 Tech Stack
- **Language:** Python  
- **Libraries:** Tkinter, psutil, Win32 APIs, matplotlib  
- **Architecture:** Event-driven system with session tracker, classifier, and analytics modules  

---

## 📈 Results
- Tracked over **1,000+ user activity events per session**  
- Blocked distractions from **40+ sites and apps**  
- Used by peers at UF for focus analytics and time management  

---

## 📸 Screenshots
-> will be adding screenshots

---

## 🔧 Setup
```bash
git clone https://github.com/KassaSana/Foco.git
cd Foco
pip install -r requirements.txt
python main.py
