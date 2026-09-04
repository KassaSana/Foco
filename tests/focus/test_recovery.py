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

    def test_future_pause_timestamp_is_preserved_as_invalid(self):
        self.manager.start_focus_session(FocusMode.QUICK_FOCUS)
        payload = json.loads(self.manager.state_file.read_text())
        payload['state'] = FocusState.PAUSED.value
        payload['pause_time'] = (self.now + timedelta(minutes=1)).isoformat()
        self.manager.state_file.write_text(json.dumps(payload))

        restored = self.new_manager()

        self.assertFalse(restored.recover_session())
        self.assertIn('future', restored.persistence_error)
        self.assertTrue(restored.state_file.exists())

    def test_corrupt_saved_session_can_be_cleared(self):
        self.manager.state_file.write_text('{broken')

        self.assertTrue(self.manager.discard_saved_session())
        self.assertFalse(self.manager.state_file.exists())
        self.assertEqual(self.manager.state, FocusState.INACTIVE)
        self.assertTrue(self.manager.start_focus_session(FocusMode.QUICK_FOCUS))

    def test_shutdown_pauses_timer_and_removes_blocking(self):
        enforcer = Mock(enforcement_active=False, has_block_entries=Mock(return_value=True))
        enforcer.last_error = ''
        enforcer.stop_enforcement.return_value = True
        manager = FocusManager(
            DataLogger(self.folder), lambda: self.now, enforcer=enforcer
        )
        manager.start_focus_session(FocusMode.QUICK_FOCUS)

        self.assertTrue(manager.shutdown())
        self.assertEqual(manager.state, FocusState.PAUSED)
        enforcer.stop_enforcement.assert_called_once_with()

    def test_shutdown_refuses_when_checkpoint_fails(self):
        manager = self.manager
        manager.start_focus_session(FocusMode.QUICK_FOCUS)
        with patch.object(manager, 'save_session_state', return_value=False):
            manager._save_pending = True
            manager.persistence_error = 'disk full'

            self.assertFalse(manager.shutdown())

        self.assertIn('disk full', manager.last_error)


if __name__ == '__main__':
    unittest.main()
