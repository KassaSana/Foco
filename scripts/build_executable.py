# App Setup Script
# Creates a Windows executable and desktop shortcut

import os
import sys
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# PyInstaller spec file content
PYINSTALLER_SPEC = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app_launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.json', '.'),
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
    name='Foco',
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
    print("Setting up Foco as a Windows application")
    print("=" * 60)
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("PyInstaller found")
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)
        print("PyInstaller installed")
    
    # Write spec file
    with open('tracker_app.spec', 'w') as f:
        f.write(PYINSTALLER_SPEC)
    print("Created PyInstaller spec file")
    
    # Build the executable
    print("Building executable... (this may take a few minutes)")
    result = subprocess.run(
        [sys.executable, '-m', 'PyInstaller', 'tracker_app.spec', '--clean'],
        check=False,
    ).returncode
    
    if result == 0:
        print("Executable created successfully")
        print("\nYour app is located at:")
        print("   dist/Foco.exe")
        
        # Check if executable exists
        exe_path = Path("dist/Foco.exe")
        if exe_path.exists():
            print(f"   Size: {exe_path.stat().st_size / (1024*1024):.1f} MB")
            
            # Create desktop shortcut option
            create_shortcut_option(exe_path)
        else:
            print("Executable not found in expected location")
    else:
        print("Build failed. Check the output above for errors.")

def create_shortcut_option(exe_path):
    """Offer to create a desktop shortcut"""
    response = input("\nCreate desktop shortcut? (y/n): ").lower().strip()
    
    if response in ['y', 'yes']:
        try:
            import win32com.client
            
            desktop = Path.home() / "Desktop"
            shortcut_path = desktop / "Foco.lnk"
            
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.Targetpath = str(exe_path.absolute())
            shortcut.WorkingDirectory = str(exe_path.parent)
            shortcut.Description = "Foco - private focus tracking and distraction blocking"
            shortcut.save()
            
            print(f"Desktop shortcut created: {shortcut_path}")
            
        except ImportError:
            print("Cannot create shortcut (win32com not available)")
            print("You can manually create a shortcut to:")
            print(f"   {exe_path.absolute()}")
        except Exception as e:
            print(f"Error creating shortcut: {e}")

def main():
    """Main setup function"""
    os.chdir(PROJECT_ROOT)
    create_app()

if __name__ == "__main__":
    main()
