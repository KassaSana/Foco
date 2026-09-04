import tempfile
import unittest
from datetime import datetime, timedelta

from foco.statistics.calculator import StatsCalculator
from foco.storage import DataLogger


class MutableClock:
    def __init__(self, value):
        self.value = value

    def now(self):
        return self.value


class TestProductivityMetrics(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.clock = MutableClock(datetime(2026, 9, 2, 12, 0))
        self.logger = DataLogger(self.temp_dir.name, self.clock.now)
        self.calculator = StatsCalculator(self.logger)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_metrics_combine_activity_quality_and_focus_completion(self):
        self.logger.replace_activities([
            {'label': 'Code', 'category': 'Building', 'duration_minutes': 50},
            {'label': 'Docs', 'category': 'Knowledge', 'duration_minutes': 20},
            {'label': 'Feed', 'category': 'pseudo_productive', 'duration_minutes': 30},
        ])
        self.logger.log_focus_session({
            'mode': 'Quick Focus', 'active_minutes': 25, 'completion_percentage': 100,
        })
        self.logger.log_focus_session({
            'mode': 'Deep Work', 'active_minutes': 30, 'completion_percentage': 33,
        })

        metrics = self.calculator.calculate_daily_stats()['metrics']

        self.assertEqual(metrics['pseudo_ratio'], 30.0)
        self.assertEqual(metrics['average_work_block'], 35.0)
        self.assertEqual(metrics['longest_work_block'], 50.0)
        self.assertEqual(metrics['focus_completion_rate'], 50.0)
        self.assertEqual(metrics['focus_minutes'], 55.0)

    def test_weekly_metrics_aggregate_multiple_daily_files(self):
        self.logger.replace_activities([
            {'label': 'Day one', 'category': 'Building', 'duration_minutes': 60}
        ])
        self.clock.value += timedelta(days=1)
        self.logger.replace_activities([
            {'label': 'Day two', 'category': 'Studying', 'duration_minutes': 30}
        ])

        monday = datetime(2026, 8, 31)
        metrics = self.calculator.calculate_weekly_stats(monday)['metrics']

        self.assertEqual(metrics['productive_minutes'], 90.0)
        self.assertEqual(metrics['longest_work_block'], 60.0)

    def test_insights_have_a_no_data_baseline(self):
        metrics = self.calculator.calculate_daily_stats()['metrics']
        self.assertTrue(self.calculator.build_insights(metrics))


if __name__ == '__main__':
    unittest.main()
