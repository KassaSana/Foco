"""Completion retries must not duplicate history or claim failed writes succeeded."""

import tempfile
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

from foco.storage import DataLogger


class TestFocusHistory(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.folder = folder.name
        self.now = datetime(2026, 9, 4, 23, 59)
        self.logger = DataLogger(self.folder, lambda: self.now)
        self.record = dict(id='session-1', history_date='2026-09-04',
                           active_minutes=25, completion_percentage=100)

    def test_replayed_completion_is_only_counted_once(self):
        self.logger.log_focus_session(self.record)
        self.logger.log_focus_session(self.record)
        reloaded = DataLogger(self.folder, lambda: self.now)
        reloaded.log_focus_session(self.record)
        self.assertEqual(len(reloaded.get_focus_sessions()), 1)
        self.assertEqual(reloaded.get_today_summary()['focus_minutes'], 25)
        self.assertEqual(reloaded.get_today_summary()['focus_sessions_completed'], 1)

    def test_next_day_retry_preserves_original_history_date(self):
        self.logger.log_focus_session(self.record)
        self.now += timedelta(days=1)
        self.logger.log_focus_session(self.record)
        self.assertEqual(self.logger.get_today_summary()['focus_sessions'], 0)
        prior = self.logger.get_day_data('2026-09-04')
        self.assertEqual(len(prior['focus_sessions']), 1)

    def test_failed_write_rolls_back_and_can_be_retried(self):
        with patch('foco.storage.Path.replace', side_effect=OSError('disk full')):
            with self.assertRaises(OSError):
                self.logger.log_focus_session(self.record)
        self.assertEqual(self.logger.get_focus_sessions(), [])
        self.assertEqual(self.logger.get_today_summary()['focus_minutes'], 0)
        self.logger.log_focus_session(self.record)
        self.assertEqual(len(DataLogger(self.folder, lambda: self.now).get_focus_sessions()), 1)

    def test_legacy_records_without_ids_are_not_deduplicated(self):
        record = dict(active_minutes=10, completion_percentage=100)
        self.logger.log_focus_session(record)
        self.logger.log_focus_session(record)
        self.assertEqual(len(self.logger.get_focus_sessions()), 2)


if __name__ == '__main__':
    unittest.main()
