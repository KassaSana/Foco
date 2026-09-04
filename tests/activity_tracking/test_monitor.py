import unittest
from datetime import datetime, timedelta

from foco.activity_tracking.monitor import ActivityMonitor


class MutableClock:
    def __init__(self, value):
        self.value = value

    def now(self):
        return self.value


class RecordingLogger:
    def __init__(self):
        self.current = None
        self.completed = []
        self.cancelled = 0

    def start_session(self, data):
        self.current = data.copy()

    def end_session(self, data):
        complete = self.current.copy()
        complete.update(data)
        self.completed.append(complete)
        self.current = None

    def cancel_current_session(self):
        self.current = None
        self.cancelled += 1


class TestActivityMonitor(unittest.TestCase):
    def setUp(self):
        self.clock = MutableClock(datetime(2026, 9, 2, 9, 0, 0))
        self.logger = RecordingLogger()
        self.window = ["chrome.exe", "Documentation"]
        self.idle_seconds = 0
        self.monitor = ActivityMonitor(
            self.logger,
            window_provider=lambda: tuple(self.window),
            idle_seconds_provider=lambda: self.idle_seconds,
            now_provider=self.clock.now,
        )

    def test_title_change_splits_same_browser_into_distinct_sessions(self):
        self.monitor.update()
        self.clock.value += timedelta(minutes=2)
        self.window[1] = "Job application"
        self.monitor.update()

        self.assertEqual(len(self.logger.completed), 1)
        self.assertEqual(self.logger.completed[0]['window_title'], "Documentation")
        self.assertEqual(self.logger.completed[0]['duration_minutes'], 2.0)
        self.assertEqual(self.logger.current['window_title'], "Job application")

    def test_idle_period_ends_session_when_idle_started(self):
        self.monitor.update()
        self.clock.value += timedelta(minutes=10)
        self.idle_seconds = 6 * 60
        self.monitor.update()

        self.assertEqual(len(self.logger.completed), 1)
        self.assertEqual(self.logger.completed[0]['duration_minutes'], 4.0)
        self.assertIsNone(self.monitor.session_start)

    def test_stop_flushes_active_session(self):
        self.monitor.update()
        self.clock.value += timedelta(minutes=1)
        self.monitor.stop()

        self.assertEqual(len(self.logger.completed), 1)
        self.assertEqual(self.logger.completed[0]['duration_minutes'], 1.0)

    def test_short_segment_is_cancelled(self):
        self.monitor.update()
        self.clock.value += timedelta(seconds=10)
        self.window[1] = "Another tab"
        self.monitor.update()

        self.assertEqual(self.logger.cancelled, 1)
        self.assertEqual(len(self.logger.completed), 0)

    def test_midnight_splits_a_session_at_the_day_boundary(self):
        self.clock.value = datetime(2026, 9, 2, 23, 58)
        self.monitor.update()
        self.clock.value = datetime(2026, 9, 3, 0, 2)
        self.monitor.update()

        self.assertEqual(self.logger.completed[0]['end_time'], '00:00:00')
        self.assertEqual(self.logger.completed[0]['duration_minutes'], 2.0)
        self.assertEqual(self.monitor.session_start, self.clock.value)


if __name__ == "__main__":
    unittest.main()
