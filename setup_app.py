# App Setup Script
# Creates a Windows executable and desktop shortcut

import os
import sys
from pathlib import Path

# PyInstaller spec file content
PYINSTALLER_SPEC = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app_launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.json', '.'),
        ('*.py', '.'),
    ],
    hiddenimports=['tkinter', 'tkinter.ttk', 'psutil', 'win32gui', 'win32process'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ADHD_Productivity_Tracker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=True,  # Request admin privileges
    icon=None
)
'''

def create_app():
    """Create the Windows executable"""
    print("🏗️ Setting up ADHD Productivity Tracker as Windows App")
    print("=" * 60)
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("✅ PyInstaller found")
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        os.system("pip install pyinstaller")
        print("✅ PyInstaller installed")
    
    # Write spec file
    with open('tracker_app.spec', 'w') as f:
        f.write(PYINSTALLER_SPEC)
    print("✅ Created PyInstaller spec file")
    
    # Build the executable
    print("🔨 Building executable... (this may take a few minutes)")
    result = os.system("pyinstaller tracker_app.spec --clean")
    
    if result == 0:
        print("✅ Executable created successfully!")
        print("\n📁 Your app is located at:")
        print("   dist/ADHD_Productivity_Tracker.exe")
        
        # Check if executable exists
        exe_path = Path("dist/ADHD_Productivity_Tracker.exe")
        if exe_path.exists():
            print(f"   Size: {exe_path.stat().st_size / (1024*1024):.1f} MB")
            
            # Create desktop shortcut option
            create_shortcut_option(exe_path)
        else:
            print("⚠️ Executable not found in expected location")
    else:
        print("❌ Build failed. Check the output above for errors.")

def create_shortcut_option(exe_path):
    """Offer to create a desktop shortcut"""
    response = input("\n🖥️ Create desktop shortcut? (y/n): ").lower().strip()
    
    if response in ['y', 'yes']:
        try:
            import win32com.client
            
            desktop = Path.home() / "Desktop"
            shortcut_path = desktop / "ADHD Productivity Tracker.lnk"
            
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.Targetpath = str(exe_path.absolute())
            shortcut.WorkingDirectory = str(exe_path.parent)
            shortcut.Description = "ADHD Productivity Tracker - Monitor your real productivity"
            shortcut.save()
            
            print(f"✅ Desktop shortcut created: {shortcut_path}")
            
        except ImportError:
            print("❌ Cannot create shortcut (win32com not available)")
            print("You can manually create a shortcut to:")
            print(f"   {exe_path.absolute()}")
        except Exception as e:
            print(f"❌ Error creating shortcut: {e}")

def create_batch_runner():
    """Create a simple batch file to run the app"""
    batch_content = '''@echo off
title ADHD Productivity Tracker
echo Starting ADHD Productivity Tracker...
echo.

cd /d "%~dp0"
python app_launcher.py

pause
'''
    
    with open('run_tracker.bat', 'w') as f:
        f.write(batch_content)
    
    print("✅ Created run_tracker.bat for easy launching")

def main():
    """Main setup function"""
    print("Choose setup option:")
    print("1. Create Windows Executable (.exe)")
    print("2. Create Batch File Runner (.bat)")
    print("3. Both")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice in ['1', '3']:
        create_app()
    
    if choice in ['2', '3']:
        create_batch_runner()
    
    print("\n🎉 Setup complete!")
    print("\n📋 Usage Instructions:")
    print("1. Run the executable with admin privileges for best window detection")
    print("2. The app will automatically track your productivity")
    print("3. Use focus timers for deep work sessions")
    print("4. All data stays local on your machine")

if __name__ == "__main__":
    main()