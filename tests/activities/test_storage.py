import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from foco.storage import DataLogger


class MutableClock:
    def __init__(self, value):
        self.value = value

    def now(self):
        return self.value


class TestActivityStorage(unittest.TestCase):
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

    def test_logger_rolls_over_to_a_new_daily_file(self):
        self.logger.replace_activities([
            {'label': 'Day one', 'category': 'Building', 'duration_minutes': 5}
        ])
        self.clock.value += timedelta(days=1)

        summary = self.logger.get_today_summary()

        self.assertEqual(summary['total_productive'], 0)
        self.assertTrue((Path(self.temp_dir.name) / '2026-09-02.json').exists())
        self.assertEqual(self.logger.current_date, '2026-09-03')

    def test_unclassified_activity_is_excluded_from_productive_summary(self):
        self.logger.replace_activities([
            {'label': 'Unknown', 'category': 'Unclassified', 'duration_minutes': 20},
            {'label': 'Code', 'category': 'Building', 'duration_minutes': 10},
        ])

        summary = self.logger.get_today_summary()

        self.assertEqual(summary['total_productive'], 10)
        self.assertEqual(summary['building'], 10)

    def test_editor_save_preserves_new_tracking_and_focus_history(self):
        self.logger.replace_activities([{'label': 'Original', 'duration_minutes': 5}])
        snapshot = self.logger.get_day_data()
        self.logger.start_session({'application': 'code.exe', 'category': 'Building'})
        self.logger.end_session({'duration_minutes': 10})
        self.logger.log_focus_session({'active_minutes': 25, 'completion_percentage': 100})
        self.logger.save_activity_edits(snapshot['date'], snapshot['sessions'], [])

        reloaded = DataLogger(self.temp_dir.name, self.clock.now)
        self.assertEqual(len(reloaded.today_data['sessions']), 1)
        self.assertEqual(reloaded.today_data['sessions'][0]['application'], 'code.exe')
        self.assertEqual(reloaded.get_today_summary()['building'], 10)
        self.assertEqual(reloaded.get_today_summary()['focus_minutes'], 25)

    def test_editor_rejects_conflicting_snapshot(self):
        self.logger.replace_activities([{'label': 'Original', 'duration_minutes': 5}])
        snapshot = self.logger.get_day_data()
        self.logger.replace_activities([{'label': 'Other edit', 'duration_minutes': 10}])
        with self.assertRaisesRegex(ValueError, 'Activities changed'):
            self.logger.save_activity_edits(snapshot['date'], snapshot['sessions'], [])
        self.assertEqual(self.logger.get_today_summary()['total_productive'], 10)

    def test_editor_rejects_yesterdays_snapshot(self):
        snapshot = self.logger.get_day_data()
        self.clock.value += timedelta(days=1)
        with self.assertRaisesRegex(ValueError, 'day has changed'):
            self.logger.save_activity_edits(snapshot['date'], [], [])

    def test_failed_editor_save_restores_memory_and_disk(self):
        self.logger.replace_activities([{'label': 'Original', 'duration_minutes': 5}])
        snapshot = self.logger.get_day_data()
        with patch('foco.storage.Path.replace', side_effect=OSError('Disk unavailable')):
            with self.assertRaises(OSError):
                self.logger.save_activity_edits(snapshot['date'], snapshot['sessions'], [])
        self.assertEqual(self.logger.get_day_data(), snapshot)
        reloaded = DataLogger(self.temp_dir.name, self.clock.now)
        self.assertEqual(reloaded.get_day_data(), snapshot)


if __name__ == '__main__':
    unittest.main()
