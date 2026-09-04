import tempfile
import unittest
from datetime import datetime, timedelta

from foco.focus.sessions import FocusManager, FocusMode, FocusState
from foco.storage import DataLogger


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


if __name__ == '__main__':
    unittest.main()
