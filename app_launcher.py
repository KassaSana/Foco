"""
App Launcher with Admin Privileges
Handles UAC prompt and launches the main application with elevated privileges
"""
import sys
import os
import ctypes
from pathlib import Path

def is_admin():
    """Check if the current process has admin privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Request admin privileges and restart the application"""
    if is_admin():
        # Already admin, run the main app
        return True
    else:
        # Request admin privileges
        try:
            # Get the path to the current script
            script_path = os.path.abspath(__file__)
            
            # Use ShellExecuteW to request admin privileges
            ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",  # Request elevation
                sys.executable,  # Python executable
                f'"{script_path}"',  # This script
                None,
                1  # Show window
            )
            return False  # Exit current process
        except Exception as e:
            print(f"Failed to request admin privileges: {e}")
            print("Running without admin privileges...")
            return True  # Continue anyway

def main():
    """Main launcher function"""
    print("🧠 ADHD Productivity Tracker")
    print("=" * 40)
    
    # Check if we need to request admin privileges
    if not run_as_admin():
        print("Requesting admin privileges...")
        sys.exit(0)  # Exit and let the elevated process take over
    
    print("✅ Running with elevated privileges")
    print("Starting productivity tracker...")
    
    # Change to the script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    try:
        # Import and run the main application
        from main import ProductivityTracker
        
        print("🚀 Launching dashboard...")
        app = ProductivityTracker()
        app.run()
        
    except ImportError as e:
        print(f"❌ Error importing modules: {e}")
        print("\nMake sure to install required packages:")
        print("pip install psutil pywin32")
        input("Press Enter to exit...")
        
    except Exception as e:
        print(f"❌ Error running application: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()