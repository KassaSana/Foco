import unittest
from unittest.mock import Mock, patch

from foco.app import FocoApp


class TestApplicationShutdown(unittest.TestCase):
    def new_app(self):
        app = FocoApp.__new__(FocoApp)
        app.dashboard = Mock()
        app.dashboard._activities_dirty = False
        app.dashboard.focus_manager.shutdown.return_value = True
        app.root = Mock()
        app.monitoring = True
        app._closing = False
        return app

    def test_close_saves_focus_before_destroying_window(self):
        app = self.new_app()

        app._close()

        app.dashboard.focus_manager.shutdown.assert_called_once_with()
        app.root.destroy.assert_called_once_with()
        self.assertFalse(app.monitoring)
        self.assertTrue(app._closing)

    def test_close_keeps_window_open_when_focus_cleanup_fails(self):
        app = self.new_app()
        app.dashboard.focus_manager.shutdown.return_value = False
        app.dashboard.focus_manager.last_error = 'Retry Disable.'

        with patch('tkinter.messagebox.showerror') as showerror:
            app._close()

        showerror.assert_called_once()
        app.root.destroy.assert_not_called()
        self.assertTrue(app.monitoring)

    def test_close_respects_unsaved_activity_cancel(self):
        app = self.new_app()
        app.dashboard._activities_dirty = True
        app.dashboard._cancel_activity_edits.side_effect = lambda: None

        app._close()

        app.dashboard._cancel_activity_edits.assert_called_once_with()
        app.dashboard.focus_manager.shutdown.assert_not_called()
        app.root.destroy.assert_not_called()


if __name__ == '__main__':
    unittest.main()
