import json
import tempfile
import unittest
from pathlib import Path

from foco.activity_tracking.classifier import CategoryEngine
from foco.config import load_config, save_config
from foco.focus.blocker import ProductivityEnforcer
from foco.focus.sessions import FocusManager, FocusMode


class TestConfiguration(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.config_path = self.root / 'config.json'

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_configuration_is_validated_normalized_and_saved(self):
        config = load_config(self.config_path)
        config['idle_timeout'] = 0
        config['pseudo_productive_limit'] = -5
        config['blocked_sites'] = ['Example.com', 'example.com', '  social.test  ']

        saved = save_config(config, self.config_path)

        self.assertEqual(saved['idle_timeout'], 1)
        self.assertEqual(saved['pseudo_productive_limit'], 0)
        self.assertEqual(saved['blocked_sites'], ['example.com', 'social.test'])
        self.assertEqual(json.loads(self.config_path.read_text())['blocked_sites'],
                         ['example.com', 'social.test'])

    def test_category_engine_reloads_user_rules(self):
        config = load_config(self.config_path)
        save_config(config, self.config_path)
        engine = CategoryEngine(self.config_path)
        self.assertEqual(engine.categorize_activity('custom.exe', 'Work'), 'Unclassified')

        config['building_apps'] = ['custom.exe']
        save_config(config, self.config_path)
        engine.reload_config()

        self.assertEqual(engine.categorize_activity('custom.exe', 'Work'), 'Building')

    def test_unknown_windows_are_unclassified_with_a_reason(self):
        config = load_config(self.config_path)
        save_config(config, self.config_path)
        engine = CategoryEngine(self.config_path)

        category, reason = engine.classify_activity('chrome.exe', 'A private dashboard')

        self.assertEqual(category, 'Unclassified')
        self.assertIn('did not match', reason)

    def test_browser_titles_match_readable_site_names(self):
        config = load_config(self.config_path)
        save_config(config, self.config_path)
        engine = CategoryEngine(self.config_path)

        category, reason = engine.classify_activity('chrome.exe', 'YouTube - music video')

        self.assertEqual(category, 'Unclassified')
        self.assertIn('Pseudo-productive', reason)

    def test_enforcer_uses_configured_block_lists(self):
        config = load_config(self.config_path)
        config['blocked_sites'] = ['only-this.test']
        config['blocked_apps'] = ['only-this.exe']
        save_config(config, self.config_path)
        hosts = self.root / 'hosts'
        hosts.write_text('127.0.0.1 localhost\n', encoding='utf-8')

        enforcer = ProductivityEnforcer(
            hosts_file=hosts,
            data_dir=self.root / 'data',
            flush_dns=False,
            config_path=self.config_path,
        )

        self.assertEqual(enforcer.blocked_sites, ['only-this.test'])
        self.assertEqual(enforcer.blocked_apps, ['only-this.exe'])

    def test_focus_manager_uses_configured_durations(self):
        config = load_config(self.config_path)
        config['focus_modes'] = {'deep_work': 75, 'quick_focus': 15}
        save_config(config, self.config_path)

        manager = FocusManager(data_logger=None, config_path=self.config_path)

        self.assertEqual(manager.durations[FocusMode.DEEP_WORK], 75)
        self.assertEqual(manager.durations[FocusMode.QUICK_FOCUS], 15)


if __name__ == '__main__':
    unittest.main()
