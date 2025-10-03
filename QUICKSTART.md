# ADHD Productivity Tracker - Quick Start

## Installation

1. Install Python 3.7+ if you don't have it already
2. Open PowerShell in the project directory
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the App

Simply run:

```
python main.py
```

## What it does

- **Automatic Tracking**: Monitors your active applications and categorizes them into Building/Studying/Applying/Knowledge
- **Pseudo-Productive Detection**: Flags YouTube videos, Reddit browsing, and other distractions
- **Focus Timer**: 90-minute Deep Work or 25-minute Quick Focus sessions
- **Time Navigation**: View your productivity by Today/Week/Month/Year
- **Local Storage**: All data stays on your machine

## First Time Use

1. Run the app and let it track for a few minutes
2. Try switching between VS Code, browser, etc. to see categorization
3. Start a focus session to test the timer
4. Data will be saved in the `productivity_data` folder

## Categories

- **Building**: VS Code, terminals, development tools
- **Studying**: PDFs, Canvas, educational sites
- **Applying**: LinkedIn (job-related), job sites, career pages
- **Knowledge**: General browsing, articles, documentation

**Pseudo-productive activities** are flagged with ⚠️ (YouTube programming videos, social media, etc.)

## Focus Sessions

- **Deep Work (90min)**: For complex coding, studying, or problem-solving
- **Quick Focus (25min)**: For smaller tasks or when attention is scattered
- Timer pauses automatically during idle time
- Shows real active work time vs total elapsed time

## Navigation

- Use the dropdown to switch between Today/Week/Month/Year views
- Use Previous/Next arrows to navigate through time periods
- Dashboard updates in real-time

## Data Storage

Data is stored locally in JSON files in the `productivity_data` folder:

- One file per day (YYYY-MM-DD.json)
- Contains sessions, categories, and daily summaries
- No data is sent anywhere - completely private

## Troubleshooting

If you get import errors:

```
pip install psutil pywin32
```

If window detection doesn't work properly, the app will still track basic activity and the focus timer will work fine.

The app is designed to be simple and functional - it tracks what you're actually doing vs what feels productive!
