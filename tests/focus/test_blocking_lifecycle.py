"""Focus and manual blocking share one owner; never use the system hosts file."""

import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

from foco.focus.blocker import ProductivityEnforcer
from foco.focus.sessions import FocusManager, FocusMode, FocusState
from foco.focus.tab import FocusTab
from foco.storage import DataLogger


class TestBlockingLifecycle(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.folder = Path(folder.name)
        self.hosts = self.folder / 'hosts'
        self.hosts.write_text('127.0.0.1 localhost\n10.0.0.2 custom.local\n')
        self.enforcer = ProductivityEnforcer(self.hosts, self.folder, flush_dns=False)
        self.enforcer.start_monitoring = Mock()
        self.clock = datetime(2026, 9, 4, 10)
        self.manager = FocusManager(DataLogger(self.folder), lambda: self.clock,
                                    enforcer=self.enforcer)

    def test_pause_unblocks_and_resume_uses_remaining_duration(self):
        self.assertTrue(self.manager.start_focus_session(FocusMode.DEEP_WORK))
        self.clock += timedelta(minutes=15)
        self.assertTrue(self.manager.pause_session())
        self.assertFalse(self.enforcer.has_block_entries())
        self.clock += timedelta(minutes=30)
        with patch.object(self.enforcer, 'start_enforcement', wraps=self.enforcer.start_enforcement) as start:
            self.assertTrue(self.manager.resume_session())
        start.assert_called_once_with(75 / 60)
        self.assertEqual(self.manager.get_remaining_time(), 75 * 60)
        self.assertTrue(self.enforcer.has_block_entries())

    def test_failed_pause_keeps_running_and_blocking_state(self):
        self.manager.start_focus_session(FocusMode.DEEP_WORK)
        with patch.object(self.enforcer, 'modify_hosts_file', return_value=False):
            self.assertFalse(self.manager.pause_session())
        self.assertEqual(self.manager.state, FocusState.RUNNING)
        self.assertTrue(self.manager.session_data['jail_active'])
        self.assertIn('retry Disable', self.manager.last_error)
        self.assertTrue(self.enforcer.state_file.exists())

    def test_failed_resume_keeps_timer_paused(self):
        self.manager.start_focus_session(FocusMode.DEEP_WORK)
        self.manager.pause_session()
        with patch.object(self.enforcer, 'modify_hosts_file', return_value=False):
            self.assertFalse(self.manager.resume_session())
        self.assertEqual(self.manager.state, FocusState.PAUSED)
        self.assertFalse(self.manager.session_data['jail_active'])

    def test_failed_start_does_not_run_unprotected_deep_work(self):
        with patch.object(self.enforcer, 'modify_hosts_file', return_value=False):
            self.assertFalse(self.manager.start_focus_session(FocusMode.DEEP_WORK))
        self.assertEqual(self.manager.state, FocusState.INACTIVE)
        self.assertTrue(self.manager.last_error)

    def test_manual_block_cannot_be_overwritten_by_focus(self):
        self.enforcer.start_enforcement(2)
        saved = self.enforcer.state_file.read_text()
        self.assertFalse(self.manager.start_focus_session(FocusMode.DEEP_WORK))
        self.assertFalse(self.enforcer.start_enforcement(4))
        self.assertEqual(self.enforcer.state_file.read_text(), saved)
        self.assertIs(self.manager.get_enforcer(), self.enforcer)

    def test_failed_stop_is_visible_and_disable_can_retry(self):
        self.manager.start_focus_session(FocusMode.DEEP_WORK)
        with patch.object(self.enforcer, 'modify_hosts_file', return_value=False):
            self.manager.end_current_session()
        self.assertTrue(self.manager.session_data['jail_active'])
        tab = FocusTab()
        tab.focus_manager = self.manager
        tab.jail_status_label = Mock()
        tab._manual_jail_active = False
        tab._update_jail_status()
        self.assertIn('retry Disable', tab.jail_status_label.config.call_args.kwargs['text'])
        with patch('foco.focus.tab.messagebox.askyesno', return_value=True):
            tab._disable_all_jail()
        self.assertFalse(self.manager.session_data['jail_active'])
        self.assertFalse(self.enforcer.has_block_entries())
        self.assertIn('custom.local', self.hosts.read_text())

    def test_failed_recovery_cleanup_is_reported(self):
        self.enforcer.modify_hosts_file(True)
        self.enforcer.save_enforcement_state(datetime.now() - timedelta(minutes=1))
        with patch.object(self.enforcer, 'modify_hosts_file', return_value=False):
            self.assertIsNone(self.enforcer.recover_enforcement())
        self.assertTrue(self.enforcer.enforcement_active)
        self.assertTrue(self.enforcer.last_error)

    def test_state_save_failure_rolls_back_hosts_change(self):
        with patch.object(self.enforcer, 'save_enforcement_state', side_effect=OSError('disk full')):
            self.assertFalse(self.enforcer.start_enforcement(1))
        self.assertFalse(self.enforcer.has_block_entries())
        self.assertFalse(self.enforcer.enforcement_active)
        self.assertIn('disk full', self.enforcer.last_error)

    def test_expired_monitor_retries_cleanup_without_terminating_apps(self):
        self.enforcer.enforcement_active = True
        self.enforcer.save_enforcement_state(datetime.now() - timedelta(minutes=1))
        with patch.object(self.enforcer, 'stop_enforcement', side_effect=[False, True]) as stop, \
                patch.object(self.enforcer, 'monitor_processes') as processes, \
                patch('foco.focus.blocker.time.sleep'):
            self.enforcer.monitor_loop()
        self.assertEqual(stop.call_count, 2)
        processes.assert_not_called()

    def test_completion_actions_can_start_another_session(self):
        tab = FocusTab()
        completion_window = Mock()
        tab._completion_window = completion_window
        tab._reset_focus_controls = Mock()
        tab._start_focus = Mock()

        tab._finish_completion('another')

        completion_window.destroy.assert_called_once_with()
        tab._reset_focus_controls.assert_called_once_with()
        tab._start_focus.assert_called_once_with()


if __name__ == '__main__':
    unittest.main()
