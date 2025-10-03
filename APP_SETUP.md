# 🚀 ADHD Productivity Tracker - Windows App Setup

## Quick Start (Recommended)

**Just double-click: `run_as_admin.bat`**

This will:

- ✅ Request admin privileges automatically
- ✅ Launch the tracker with best window detection
- ✅ Show a nice console interface

## Setup Options

### Option 1: Batch File (Simplest)

Just use `run_as_admin.bat` - double-click and you're done!

### Option 2: Create Windows Executable

```bash
python setup_app.py
```

This creates a standalone .exe file that:

- Runs without needing Python installed
- Automatically requests admin privileges
- Can be shared with friends easily

### Option 3: Python Direct (Manual)

```bash
python app_launcher.py
```

## Why Admin Privileges?

Admin privileges help the tracker:

- 🎯 **Better window detection** - See all application names and titles
- 📊 **Accurate activity monitoring** - Track all processes properly
- 🔒 **Complete system access** - Monitor productivity across all apps

_Don't worry - all data stays local on your machine!_

## Files Created

- `app_launcher.py` - Smart launcher with admin request
- `run_as_admin.bat` - One-click admin launcher (easiest!)
- `setup_app.py` - Creates standalone .exe
- `create_manifest.py` - Windows admin manifest

## Installation

1. **Install dependencies** (if not done):

   ```bash
   pip install psutil pywin32
   ```

2. **Launch the app**:

   ```bash
   # Easiest way:
   run_as_admin.bat

   # Or manually:
   python app_launcher.py
   ```

## Features

✅ **Automatic UAC prompt** - Requests admin when needed  
✅ **Smart window detection** - Tracks all applications  
✅ **Professional console** - Nice startup messages  
✅ **Error handling** - Graceful failure if admin denied  
✅ **Easy sharing** - Create .exe for friends

## Sharing with Friends

**Option A**: Share the whole folder

- They just double-click `run_as_admin.bat`
- Need Python installed

**Option B**: Create executable

- Run `python setup_app.py`
- Share the `.exe` file from `dist/` folder
- No Python needed on their machine!

## Troubleshooting

**"Access Denied" errors**:

- Make sure to allow the UAC prompt
- Try running PowerShell as admin first

**Import errors**:

- Run: `pip install psutil pywin32`

**Window detection not working**:

- Make sure you allowed admin privileges
- Some security software blocks window monitoring

The app is now ready to run as a proper Windows application! 🎉
