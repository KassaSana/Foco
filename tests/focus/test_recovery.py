import json
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

from foco.focus.sessions import FocusManager, FocusMode, FocusState
from foco.storage import DataLogger


class TestFocusRecovery(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.folder = folder.name
        self.now = datetime(2026, 9, 4, 10)
        self.manager = self.new_manager()

    def new_manager(self):
        return FocusManager(DataLogger(self.folder, lambda: self.now), lambda: self.now)

    def test_running_session_restores_deadline_and_original_target(self):
        self.manager.start_focus_session(FocusMode.QUICK_FOCUS)
        self.now += timedelta(minutes=5)
        restored = self.new_manager()
        restored.durations[FocusMode.QUICK_FOCUS] = 1
        self.assertTrue(restored.recover_session())
        self.assertEqual(restored.state, FocusState.RUNNING)
        self.assertEqual(restored.get_remaining_time(), 20 * 60)

    def test_paused_session_does_not_count_time_while_closed(self):
        self.manager.start_focus_session(FocusMode.QUICK_FOCUS)
        self.now += timedelta(minutes=5)
        self.manager.pause_session()
        self.now += timedelta(hours=1)
        restored = self.new_manager()
        restored.recover_session()
        self.assertEqual(restored.state, FocusState.PAUSED)
        self.assertEqual(restored.get_remaining_time(), 20 * 60)
        restored.resume_session()
        self.assertEqual(restored.get_remaining_time(), 20 * 60)

    def test_expired_session_records_target_time_not_downtime(self):
        self.manager.start_focus_session(FocusMode.QUICK_FOCUS)
        self.now += timedelta(days=1)
        restored = self.new_manager()
        restored.recover_session()
        self.assertEqual(restored.state, FocusState.COMPLETED)
        history = restored.data_logger.get_day_data('2026-09-04')['focus_sessions']
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['active_minutes'], 25)
        self.assertEqual(history[0]['end_time'], '10:25:00')
        self.assertFalse(restored.state_file.exists())

    def test_crash_after_history_save_does_not_duplicate_completion(self):
        self.manager.start_focus_session(FocusMode.QUICK_FOCUS)
        self.now += timedelta(minutes=25)
        with patch('foco.focus.sessions.Path.unlink', side_effect=OSError('busy')):
            self.manager.update()
        self.assertTrue(self.manager._completion_pending)
        restored = self.new_manager()
        restored.recover_session()
        self.assertEqual(len(restored.data_logger.get_focus_sessions()), 1)
        self.assertFalse(restored.state_file.exists())

    def test_failed_completion_is_retried_without_losing_timer_record(self):
        self.manager.start_focus_session(FocusMode.QUICK_FOCUS)
        self.now += timedelta(minutes=25)
        with patch.object(self.manager.data_logger, 'log_focus_session', side_effect=OSError('full')):
            self.manager.update()
        self.assertTrue(self.manager.persistence_error)
        self.assertFalse(self.manager.start_focus_session(FocusMode.QUICK_FOCUS))
        restored = self.new_manager()
        restored.recover_session()
        self.assertEqual(len(restored.data_logger.get_focus_sessions()), 1)

    def test_failed_pause_checkpoint_is_retried(self):
        self.manager.start_focus_session(FocusMode.QUICK_FOCUS)
        with patch('foco.focus.sessions.Path.replace', side_effect=OSError('full')):
            self.manager.pause_session()
        self.assertTrue(self.manager.persistence_error)
        self.manager.update()
        restored = self.new_manager()
        restored.recover_session()
        self.assertEqual(restored.state, FocusState.PAUSED)

    def test_invalid_saved_state_is_preserved_and_not_overwritten(self):
        self.manager.state_file.write_text('{broken')
        self.assertFalse(self.manager.recover_session())
        self.assertFalse(self.manager.start_focus_session(FocusMode.QUICK_FOCUS))
        self.assertEqual(self.manager.state_file.read_text(), '{broken')

    def test_missing_deep_work_block_recovers_paused(self):
        self.manager.start_focus_session(FocusMode.QUICK_FOCUS)
        payload = json.loads(self.manager.state_file.read_text())
        payload['session']['mode'] = FocusMode.DEEP_WORK.value
        self.manager.state_file.write_text(json.dumps(payload))
        restored = self.new_manager()
        restored.jail_enforcer = Mock(enforcement_active=False)
        restored.recover_session()
        self.assertEqual(restored.state, FocusState.PAUSED)
        self.assertFalse(restored.session_data['jail_active'])


if __name__ == '__main__':
    unittest.main()
