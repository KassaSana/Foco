import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from foco.config import load_config, save_config
from foco.distraction_budget import DistractionBudget
from foco.storage import DataLogger


class MutableClock:
    def __init__(self, value):
        self.value = value

    def now(self):
        return self.value


class TestDistractionBudget(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.clock = MutableClock(datetime(2026, 9, 4, 10, 0))
        self.config_path = Path(self.temp_dir.name) / "config.json"
        config = load_config(self.config_path)
        config["pseudo_productive_limit"] = 10
        save_config(config, self.config_path)
        self.logger = DataLogger(self.temp_dir.name, self.clock.now)
        self.budget = DistractionBudget(self.logger, self.config_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_active_pseudo_time_counts_toward_threshold(self):
        self.logger.replace_activities([
            {"label": "Reddit", "category": "pseudo_productive", "duration_minutes": 9}
        ])

        status = self.budget.get_status(active_pseudo_minutes=1)

        self.assertEqual(status["used_minutes"], 10)
        self.assertTrue(status["should_alert"])
        self.assertEqual(status["progress_percentage"], 100)

    def test_acknowledgement_persists_across_restart(self):
        self.logger.replace_activities([
            {"label": "Reddit", "category": "pseudo_productive", "duration_minutes": 12}
        ])
        self.budget.acknowledge_alert()

        reloaded_logger = DataLogger(self.temp_dir.name, self.clock.now)
        reloaded_budget = DistractionBudget(reloaded_logger, self.config_path)
        status = reloaded_budget.get_status()

        self.assertTrue(status["crossed"])
        self.assertTrue(status["alerted"])
        self.assertFalse(status["should_alert"])

    def test_new_day_resets_usage_and_alert(self):
        self.logger.replace_activities([
            {"label": "Reddit", "category": "pseudo_productive", "duration_minutes": 12}
        ])
        self.budget.acknowledge_alert()
        self.clock.value += timedelta(days=1)

        status = self.budget.get_status()

        self.assertEqual(status["used_minutes"], 0)
        self.assertFalse(status["alerted"])
        self.assertFalse(status["should_alert"])

    def test_zero_limit_disables_alerts(self):
        config = load_config(self.config_path)
        config["pseudo_productive_limit"] = 0
        save_config(config, self.config_path)
        self.budget.reload_config()

        status = self.budget.get_status(active_pseudo_minutes=30)

        self.assertFalse(status["enabled"])
        self.assertFalse(status["should_alert"])


if __name__ == "__main__":
    unittest.main()
