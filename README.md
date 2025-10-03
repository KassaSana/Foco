🧠 Simple ADHD Productivity Tracker
A no-bullshit productivity tracker for CS students with ADHD. Tracks what you're ACTUALLY working on vs what feels productive.
Why This Exists
Traditional productivity apps don't work for ADHD brains. This tool:

Distinguishes REAL work from pseudo-productive activities
Tracks 4 core categories automatically
Catches you watching "motivational" CS videos instead of coding
Two simple focus modes: Deep Work (90min) or Quick Focus (25min)
Shows actual keyboard/mouse activity, not just elapsed time

What Gets Tracked
🔨 Building
Real work: VS Code with active coding, terminal usage, Git commits, file modifications
Flagged: IDE open but no activity >5min, just browsing code
📚 Studying
Real work: Canvas active, PDF readers with course materials, note-taking, problem sets
Flagged: Passive reading without engagement
🎯 Applying
Real work: Job applications, LinkedIn messaging, resume editing, company research
Flagged: LinkedIn feed scrolling >10min, watching career advice videos
🧠 Knowledge Building
Real work: Quality articles, technical documentation, books, educational content
Flagged: Endless Wikipedia rabbit holes, social media disguised as "learning"
Activity Detection Examples
✅ PRODUCTIVE
Building: VS Code (React project) - 2.1h active coding
Studying: Canvas Quiz - 45min, PDF notes - 30min  
Applying: 3 job applications, 2 recruiter messages
Knowledge: Gaza conflict article - 20min focused reading

❌ PSEUDO-PRODUCTIVE (Gets Flagged)
"10x Developer Tips" YouTube - 45min
Reddit programming discussions - 1.2h
LinkedIn feed scrolling - 35min
"How to Get Better at Coding" videos - 1h
Quick Start

python main.py
Pick your focus mode:

Deep Work (90min) - Complex coding, studying, problem-solving
Quick Focus (25min) - Small tasks, quick wins

Work normally - it tracks automatically
See your real vs pseudo-productive time

Dashboard Overview
Today View
Today's Real Work: 6.2 hours
├─ Building: 3.1h (VS Code: 2.8h, Terminal: 0.3h)
├─ Studying: 1.8h (Canvas: 1.2h, PDF Reader: 0.6h)  
├─ Applying: 1.3h (Job sites: 0.8h, LinkedIn: 0.5h)
└─ Knowledge: 0h

Pseudo-Productive Time: 47 minutes
└─ YouTube CS videos (23min), Tech Twitter (15min), Reddit (9min)

Current Activity: VS Code - Building (Active: 12min)
Context Switches: 3 today
This Week View
This Week: 31.4 productive hours (avg 4.5h/day)
Mon ████████░░ 6.2h Thu ███████░░░ 5.1h  
Tue ██████░░░░ 4.8h Fri ████████░░ 6.0h
Wed █████░░░░░ 3.7h Sat ███░░░░░░░ 2.1h
Sun █████░░░░░ 3.5h

Top Category: Building (18.2h) - React project momentum
Biggest Distraction: YouTube (2.3h total)
Best Day: Monday (6.2h productive)
This Month View
September 2024: 127 productive hours
Week 1: ████████░░ 28.3h Week 3: ██████░░░░ 22.1h
Week 2: ████████░░ 31.4h Week 4: ███████░░░ 25.2h

Monthly Breakdown:
├─ Building: 72h (57%) - Consistent coding habit
├─ Studying: 31h (24%) - Exam season spike  
├─ Applying: 18h (14%) - Job search active
└─ Knowledge: 6h (5%) - Light learning

Trends: +15% vs August, fewer context switches
Year View
2024 Progress: 1,847 productive hours
Q1 ██████░░░░ 445h Q3 ████████░░ 521h
Q2 ███████░░░ 454h Q4 ███████░░░ 427h (projected)

Yearly Insights:

- Best Month: September (127h)
- Growth: +23% vs 2023 same period
- Building Skills: 1,089h total
- Consistency: 73% of days had >2h productive work
  Installation
  bash# Requirements: Python 3.7+
  pip install psutil

# Run

python main.py
Features
Smart Detection

Application Monitoring: Tracks active windows and keyboard/mouse activity
Website Categorization: Automatically sorts productive vs pseudo-productive sites
Context Switching Alerts: Warns when jumping between tasks too frequently
Idle Detection: Pauses tracking when inactive >5min

Focus Modes

Deep Work (90min): For complex tasks requiring sustained attention
Quick Focus (25min): For smaller tasks or when attention is scattered
Real Activity Progress: Shows actual work done vs just time passed
Gentle Notifications: ADHD-friendly reminders, not harsh interruptions

Anti-Procrastination

Pseudo-Productive Flagging: Catches "learning" that's actually procrastination
YouTube CS Video Detection: Flags motivational/educational content consumption
Social Media Alerts: Warns when browsing disguised as "research"
Context Switch Tracking: Monitors task-jumping behavior

Configuration
Basic settings in config.json:
json{
"focus_modes": {
"deep_work": 90,
"quick_focus": 25
},
"idle_timeout": 5,
"pseudo_productive_limit": 10
}
Technical Architecture
Core Components

ActivityMonitor: Real-time app/website tracking
CategoryEngine: Smart activity categorization
FocusManager: Timer and session management
DataLogger: Local storage of productivity data

Detection Logic

Building: IDE activity + file changes + terminal usage
Studying: Educational sites + note-taking + active engagement
Applying: Job sites + professional networking + applications
Knowledge: Quality content + focused reading + educational sites

Privacy

Local Only: All data stored on your machine
No Screenshots: Only tracks app names and activity levels
No Content Reading: Doesn't see what you're typing/reading

Project Structure
├── main.py # Application entry point
├── activity_monitor.py # Real-time activity detection
├── category_engine.py # Smart categorization logic  
├── focus_manager.py # Focus sessions and timers
├── dashboard.py # Productivity dashboard with time navigation
├── data_logger.py # Local data storage and retrieval
├── stats_calculator.py # Historical summaries and analytics
├── trend_analyzer.py # Growth tracking and insights
└── config.json # Basic configuration

🏗️ DESIGN DOCUMENT FOR CLAUDE
Technical Requirements
Build a single desktop application with these exact specifications:

1. Core Functionality
   Activity Monitoring System:

Monitor active windows and applications in real-time
Track keyboard/mouse activity to distinguish active vs idle time
Categorize activities into: Building, Studying, Applying, Knowledge Building
Detect and flag pseudo-productive activities

Smart Categorization Rules:
pythonBUILDING_APPS = ['code.exe', 'idea64.exe', 'pycharm64.exe', 'cmd.exe', 'terminal']
STUDYING_APPS = ['canvas', 'pdf_reader', 'notion', 'onenote']  
APPLYING_SITES = ['linkedin.com', 'indeed.com', 'glassdoor.com']
PSEUDO_PRODUCTIVE = ['youtube.com/watch', 'reddit.com', 'twitter.com']
Focus Timer System:

Two modes only: Deep Work (90min), Quick Focus (25min)
Show real activity progress vs elapsed time
Pause timer during idle periods
End-of-session summary with category breakdown

2. User Interface
   Simple Dashboard Layout:
   [Header: ADHD Productivity Tracker] [Today: Mon Sep 30] [View: Today ▼]

[Real Work: 6.2h] [Pseudo: 47m] [Sessions: 3] [Switches: 12]

Activity Breakdown:
├─ Building: 3.1h ████████░░ (VS Code, Terminal)
├─ Studying: 1.8h █████░░░░░ (Canvas, PDFs)  
├─ Applying: 1.3h ████░░░░░░ (LinkedIn, Job Sites)
└─ Knowledge: 0h ░░░░░░░░░░

Current: VS Code - React Project (Building) ⏱️ 12:34

[◀ Previous Day] [Deep Work 90min] [Quick Focus 25min] [Next Day ▶]
Time Period Navigation:

Dropdown menu: Today | This Week | This Month | This Year
Arrow navigation for previous/next periods
Quick insights and trends for each time period
Consistent layout across all views

No Complex UI Elements:

No tabs, menus, or navigation
Single screen with all info visible
Large, clear buttons for focus modes
Color-coded categories (green=good, orange=caution, red=problematic)

3. Implementation Details
   Required Libraries:
   pythonimport psutil # Process monitoring
   import time # Time tracking  
   import json # Data storage
   import tkinter # Simple GUI
   from datetime import datetime, timedelta
   Core Classes Needed:

ActivityMonitor - tracks active windows and applications
CategoryEngine - categorizes activities and detects pseudo-productive time
FocusSession - manages 90min/25min focus sessions
ProductivityDashboard - simple GUI with time period navigation
DataLogger - saves/loads productivity data locally
StatsCalculator - generates daily/weekly/monthly/yearly summaries
TrendAnalyzer - calculates growth, consistency, and insights

Key Features to Implement:

Real-time window title and process name detection
Keyboard/mouse activity monitoring (idle detection)
Website URL extraction from browser titles
Local JSON data storage with historical summaries
Time period navigation (Today/Week/Month/Year views)
Statistics calculation across different time periods
Trend analysis and growth tracking
Focus session timer with pause/resume
Historical data aggregation and insights

4. Data Structure
   Data Structure:
   json{
   "date": "2024-09-30",
   "sessions": [
   {
   "start_time": "09:15:00",
   "end_time": "10:45:00",
   "category": "Building",
   "application": "VS Code",
   "project": "React App",
   "active_time": 78,
   "total_time": 90
   }
   ],
   "daily_summary": {
   "building": 185,
   "studying": 108,
   "applying": 78,
   "knowledge": 0,
   "pseudo_productive": 47,
   "context_switches": 12,
   "total_productive": 371
   }
   }
   Historical Data Structure:
   json{
   "weekly_summaries": {
   "2024-W39": {
   "total_productive": 1847,
   "building": 1089,
   "studying": 445,
   "applying": 213,
   "knowledge": 100,
   "daily_averages": 4.2,
   "best_day": "2024-09-30",
   "consistency": 0.73
   }
   },
   "monthly_summaries": {
   "2024-09": {
   "total_productive": 7623,
   "trend_vs_previous": "+15%",
   "top_category": "Building",
   "biggest_distraction": "YouTube"
   }
   },
   "yearly_summaries": {
   "2024": {
   "total_productive": 89472,
   "growth_vs_previous": "+23%",
   "best_month": "September",
   "quarterly_breakdown": [445, 454, 521, 427]
   }
   }
   }
5. Anti-Procrastination Logic
   Pseudo-Productive Detection:

YouTube videos about programming/productivity
Reddit browsing (even programming subreddits)
Twitter/social media consumption
"Learning" content without practical application
Motivational/inspirational content consumption

Context Switching Detection:

Count app switches per hour
Alert if >15 switches/hour
Track time spent in each application
Flag rapid task-jumping patterns

6. ADHD-Specific Accommodations
   Interface Design:

Minimal cognitive load
No overwhelming statistics or charts
Clear visual feedback on current activity
Gentle notifications, not intrusive alerts

Functionality:

Automatic pause during idle periods
Focus on consistency over perfection
Celebrate small wins and progress
Simple binary feedback (productive vs not)

Build Instructions for Claude
Create a single Python application that:

Monitors computer activity in real-time
Categorizes work into 4 types automatically
Provides 2 focus timer modes
Shows productivity dashboard with time period navigation (Today/Week/Month/Year)
Flags pseudo-productive activities
Stores all data locally with historical summaries
Calculates trends, growth, and insights across time periods

Priority Order:

Basic activity monitoring and categorization
Simple GUI dashboard showing current stats
Time period navigation and historical data storage
Focus timer functionality (90min/25min)
Historical summaries and trend analysis
Pseudo-productive activity flagging

Keep it simple and functional. Better to have basic features working perfectly than complex features half-implemented.
