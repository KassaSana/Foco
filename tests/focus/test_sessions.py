import tempfile
import unittest
from datetime import datetime, timedelta

from foco.focus.sessions import FocusManager, FocusMode, FocusState
from foco.config import save_config
from foco.storage import DataLogger
from pathlib import Path


class MutableClock:
    def __init__(self, value):
        self.value = value

    def now(self):
        return self.value


class TestFocusSessions(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.clock = MutableClock(datetime(2026, 9, 2, 10, 0, 0))
        self.logger = DataLogger(self.temp_dir.name, self.clock.now)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_focus_session_auto_completes_and_is_persisted(self):
        manager = FocusManager(self.logger, self.clock.now)
        manager.durations[FocusMode.QUICK_FOCUS] = 1
        manager.start_focus_session(FocusMode.QUICK_FOCUS)
        self.clock.value += timedelta(minutes=1)

        result = manager.update()

        self.assertEqual(manager.state, FocusState.COMPLETED)
        self.assertEqual(result['completion_percentage'], 100)
        self.assertEqual(len(self.logger.get_focus_sessions()), 1)
        self.assertEqual(self.logger.get_today_summary()['focus_sessions_completed'], 1)

    def test_pause_freezes_remaining_time_until_resume(self):
        manager = FocusManager(self.logger, self.clock.now)
        manager.start_focus_session(FocusMode.QUICK_FOCUS)
        self.clock.value += timedelta(minutes=5)
        manager.pause_session()
        paused_remaining = manager.get_remaining_time()
        self.clock.value += timedelta(minutes=10)

        self.assertEqual(manager.get_remaining_time(), paused_remaining)
        manager.resume_session()
        self.assertEqual(round(manager.get_remaining_time()), round(paused_remaining))

    def test_settings_change_only_affects_the_next_session(self):
        config = Path(self.temp_dir.name) / 'config.json'
        save_config({'focus_modes': {'quick_focus': 25, 'deep_work': 90}}, config)
        manager = FocusManager(self.logger, self.clock.now, config_path=config)
        manager.start_focus_session(FocusMode.QUICK_FOCUS)
        self.clock.value += timedelta(minutes=5)
        save_config({'focus_modes': {'quick_focus': 1, 'deep_work': 90}}, config)
        manager.reload_config()
        manager.update()

        self.assertEqual(manager.state, FocusState.RUNNING)
        self.assertEqual(manager.get_remaining_time(), 20 * 60)
        self.assertEqual(manager.get_progress_percentage(), 20)
        self.assertEqual(manager.get_session_info()['target_minutes'], 25)
        manager.pause_session()
        self.clock.value += timedelta(minutes=10)
        self.assertEqual(manager.get_remaining_time(), 20 * 60)
        manager.resume_session()
        self.clock.value += timedelta(minutes=20)
        result = manager.update()
        self.assertEqual(result['duration_minutes'], 25)
        self.assertEqual(result['completion_percentage'], 100)

        manager.start_focus_session(FocusMode.QUICK_FOCUS)
        self.assertEqual(manager.get_remaining_time(), 60)

    def test_stopping_just_before_target_is_not_counted_as_completed(self):
        manager = FocusManager(self.logger, self.clock.now)
        manager.durations[FocusMode.QUICK_FOCUS] = 1
        manager.start_focus_session(FocusMode.QUICK_FOCUS)
        self.clock.value += timedelta(seconds=59.9)
        result = manager.end_current_session()
        self.assertLess(result['completion_percentage'], 100)
        self.assertEqual(self.logger.get_today_summary()['focus_sessions_completed'], 0)

    def test_timer_info_preserves_second_precision(self):
        manager = FocusManager(self.logger, self.clock.now)
        manager.durations[FocusMode.QUICK_FOCUS] = 1
        manager.start_focus_session(FocusMode.QUICK_FOCUS)
        self.clock.value += timedelta(seconds=7)
        info = manager.get_session_info()
        self.assertEqual(info['remaining_seconds'], 53)
        self.assertEqual(manager.format_time(info['remaining_seconds']), '00:53')


if __name__ == '__main__':
    unittest.main()
