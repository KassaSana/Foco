import json
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from foco.data_logger import DataLogger
from foco.focus_manager import FocusManager, FocusMode, FocusState


class MutableClock:
    def __init__(self, value):
        self.value = value

    def now(self):
        return self.value


class TestPersistence(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.clock = MutableClock(datetime(2026, 9, 2, 10, 0, 0))
        self.logger = DataLogger(self.temp_dir.name, self.clock.now)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_manual_activity_edits_become_canonical_and_recalculate_summary(self):
        self.logger.replace_activities([
            {'start_time': '09:00', 'end_time': '09:30', 'label': 'Project',
             'category': 'Building', 'duration_minutes': '30'},
            {'start_time': '09:30', 'end_time': '09:40', 'label': 'Reddit',
             'category': 'pseudo_productive', 'duration_minutes': '10'},
        ])

        summary = self.logger.get_today_summary()
        self.assertEqual(summary['building'], 30)
        self.assertEqual(summary['pseudo_productive'], 10)
        self.assertEqual(summary['total_productive'], 30)
        reloaded = DataLogger(self.temp_dir.name, self.clock.now)
        self.assertEqual(len(reloaded.get_recent_activities()), 2)

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

    def test_logger_rolls_over_to_a_new_daily_file(self):
        self.logger.replace_activities([
            {'label': 'Day one', 'category': 'Building', 'duration_minutes': 5}
        ])
        self.clock.value += timedelta(days=1)

        summary = self.logger.get_today_summary()

        self.assertEqual(summary['total_productive'], 0)
        self.assertTrue((Path(self.temp_dir.name) / '2026-09-02.json').exists())
        self.assertEqual(self.logger.current_date, '2026-09-03')

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
