"""Foco dependency and first-run setup utility."""
import subprocess
import sys
import os
import importlib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

def check_python():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("Python 3.7+ required. Current version:", sys.version)
        return False
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    return True

def install_packages():
    """Install required packages"""
    packages = ['psutil', 'pywin32']
    
    print("Installing required packages...")
    
    for package in packages:
        try:
            __import__(package)
            print(f"{package} already installed")
        except ImportError:
            print(f"Installing {package}...")
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                             check=True, capture_output=True, text=True)
                print(f"{package} installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"Failed to install {package}: {e}")
                return False
    
    return True

def create_desktop_shortcut():
    """Create desktop shortcut to the batch file"""
    try:
        desktop = Path.home() / "Desktop"
        shortcut_name = "Foco"
        
        # Create a simple .bat file on desktop that calls our main bat
        batch_content = f'''@echo off
cd /d "{PROJECT_ROOT}"
call run_as_admin.bat
'''
        
        desktop_bat = desktop / f"{shortcut_name}.bat"
        with open(desktop_bat, 'w') as f:
            f.write(batch_content)
        
        print(f"Desktop shortcut created: {desktop_bat}")
        return True
        
    except Exception as e:
        print(f"Could not create desktop shortcut: {e}")
        return False

def setup_data_folder():
    """Ensure data folder exists"""
    data_folder = PROJECT_ROOT / "productivity_data"
    data_folder.mkdir(exist_ok=True)
    print(f"Data folder ready: {data_folder.absolute()}")

def test_imports():
    """Test all module imports"""
    modules = [
        'tkinter', 'psutil', 'json', 'datetime', 
        'foco.main', 'foco.dashboard', 'foco.activity_monitor',
        'foco.category_engine', 'foco.data_logger'
    ]
    
    print("Testing module imports...")
    
    for module in modules:
        try:
            if module == 'tkinter':
                import tkinter
            else:
                importlib.import_module(module)
            print(f"{module}")
        except ImportError as e:
            print(f"{module}: {e}")
            return False
    
    return True

def main():
    """Main installer function"""
    print("Foco - Setup and Installation")
    print("=" * 55)
    
    # Check Python version
    if not check_python():
        input("Press Enter to exit...")
        return
    
    # Install packages
    if not install_packages():
        print("Package installation failed")
        input("Press Enter to exit...")
        return
    
    # Setup data folder
    setup_data_folder()
    
    # Test imports
    if not test_imports():
        print("Some modules failed to import")
        input("Press Enter to continue anyway...")
    
    # Offer desktop shortcut
    response = input("\nCreate desktop shortcut? (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        create_desktop_shortcut()
    
    print("\nInstallation complete")
    print("\nNext Steps:")
    print("1. Double-click 'run_as_admin.bat' to start the tracker")
    print("2. Allow admin privileges when prompted (for better tracking)")
    print("3. The tracker will start automatically monitoring")
    print("4. Use focus timers for deep work sessions")
    
    print("\nYour data is stored in: productivity_data/")
    print("Everything stays private on your machine")
    
    # Ask if they want to run now
    response = input("\nLaunch Foco now? (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        print("\n Starting tracker...")
        subprocess.run([sys.executable, str(PROJECT_ROOT / 'app_launcher.py')], cwd=PROJECT_ROOT)

if __name__ == "__main__":
    main()
