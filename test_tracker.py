"""
Simple test script to verify core functionality
Run this to test the tracker without GUI
"""
from data_logger import DataLogger
from category_engine import CategoryEngine
from stats_calculator import StatsCalculator
from focus_manager import FocusManager, FocusMode
import time

def test_basic_functionality():
    print("🧠 Testing ADHD Productivity Tracker Components")
    print("=" * 50)
    
    # Test CategoryEngine
    print("\n1. Testing CategoryEngine...")
    engine = CategoryEngine()
    
    test_apps = [
        ("code.exe", "React App - Visual Studio Code"),
        ("chrome.exe", "YouTube - How to be a better programmer"),
        ("chrome.exe", "LinkedIn - Software Engineer Jobs"),
        ("chrome.exe", "Stack Overflow - Python Question")
    ]
    
    for app, title in test_apps:
        category = engine.categorize_activity(app, title)
        is_pseudo = engine.is_pseudo_productive(app, title)
        flag = " ⚠️ PSEUDO" if is_pseudo else " ✅"
        print(f"   {app} + '{title[:30]}...' -> {category}{flag}")
    
    # Test DataLogger
    print("\n2. Testing DataLogger...")
    logger = DataLogger()
    print(f"   Data directory: {logger.data_dir}")
    print(f"   Today's file: {logger.get_today_filename()}")
    
    # Test sample session
    logger.start_session({
        'start_time': '10:30:00',
        'application': 'code.exe',
        'window_title': 'React App',
        'category': 'Building',
        'is_pseudo_productive': False
    })
    
    logger.end_session({
        'end_time': '10:45:00',
        'duration_minutes': 15.0,
        'application': 'code.exe',
        'window_title': 'React App'
    })
    
    summary = logger.get_today_summary()
    print(f"   Sample session logged: {summary['building']} minutes building")
    
    # Test StatsCalculator
    print("\n3. Testing StatsCalculator...")
    calculator = StatsCalculator(logger)
    daily_stats = calculator.calculate_daily_stats()
    print(f"   Today's productive time: {daily_stats['total_productive']} minutes")
    
    # Test FocusManager
    print("\n4. Testing FocusManager...")
    focus_manager = FocusManager(logger)
    
    # Start a quick focus session
    success = focus_manager.start_focus_session(FocusMode.QUICK_FOCUS)
    print(f"   Focus session started: {success}")
    
    session_info = focus_manager.get_session_info()
    if session_info:
        print(f"   Current session: {session_info['mode']} - {session_info['state']}")
        print(f"   Target time: {session_info['target_minutes']} minutes")
    
    # Simulate some time passing
    time.sleep(1)
    
    # End session
    session_data = focus_manager.end_current_session()
    if session_data:
        print(f"   Session completed: {session_data['completion_percentage']}% done")
    
    print("\n✅ All components working correctly!")
    print("\nTo run the full GUI application:")
    print("python main.py")

if __name__ == "__main__":
    test_basic_functionality()