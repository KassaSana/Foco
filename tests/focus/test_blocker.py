import tempfile
import json
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from foco.focus.blocker import ProductivityEnforcer


class TestProductivityEnforcer(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.hosts = self.root / "hosts"
        self.hosts.write_text("127.0.0.1 localhost\n10.0.0.2 custom.local\n", encoding="utf-8")
        self.enforcer = ProductivityEnforcer(
            hosts_file=self.hosts,
            data_dir=self.root / "data",
            flush_dns=False,
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_blocking_is_idempotent_and_preserves_user_entries(self):
        self.assertTrue(self.enforcer.backup_hosts_file())
        self.assertTrue(self.enforcer.modify_hosts_file(block=True))
        self.assertTrue(self.enforcer.modify_hosts_file(block=True))

        content = self.hosts.read_text(encoding="utf-8")
        self.assertEqual(content.count(self.enforcer.BLOCK_START), 1)
        self.assertIn("10.0.0.2 custom.local", content)

        self.assertTrue(self.enforcer.modify_hosts_file(block=False))
        cleaned = self.hosts.read_text(encoding="utf-8")
        self.assertNotIn(self.enforcer.BLOCK_START, cleaned)
        self.assertIn("10.0.0.2 custom.local", cleaned)

    def test_recovery_cleans_expired_enforcement(self):
        self.enforcer.modify_hosts_file(block=True)
        self.enforcer.save_enforcement_state(datetime.now() - timedelta(minutes=1))

        self.assertIsNone(self.enforcer.recover_enforcement())
        self.assertFalse(self.enforcer.state_file.exists())
        self.assertFalse(self.enforcer.has_block_entries())

    def test_recovery_resumes_live_enforcement(self):
        end_time = datetime.now() + timedelta(minutes=10)
        self.enforcer.modify_hosts_file(block=True)
        self.enforcer.save_enforcement_state(end_time)

        recovered = self.enforcer.recover_enforcement()
        self.assertEqual(recovered, end_time)
        self.assertTrue(self.enforcer.enforcement_active)

    def test_recovery_restores_original_rules_after_settings_change(self):
        self.enforcer.blocked_sites = ['original.example']
        self.enforcer.blocked_apps = ['original.exe']
        end_time = datetime.now() + timedelta(minutes=10)
        self.enforcer.save_enforcement_state(end_time)
        recovered = ProductivityEnforcer(self.hosts, self.root / 'data', flush_dns=False)
        recovered.blocked_sites = ['different.example']
        recovered.blocked_apps = ['different.exe']
        self.assertEqual(recovered.recover_enforcement(), end_time)
        self.assertEqual(recovered.blocked_apps, ['original.exe'])
        content = self.hosts.read_text()
        self.assertIn('original.example', content)
        self.assertNotIn('different.example', content)
        self.assertIn('custom.local', content)

    def test_legacy_saved_block_uses_configured_rules(self):
        end_time = datetime.now() + timedelta(minutes=10)
        self.enforcer.state_file.write_text(json.dumps({
            'active': True, 'end_time': end_time.isoformat()
        }))
        expected = list(self.enforcer.blocked_apps)
        self.assertEqual(self.enforcer.recover_enforcement(), end_time)
        self.assertEqual(self.enforcer.blocked_apps, expected)

    def test_invalid_saved_rules_do_not_modify_hosts(self):
        self.enforcer.save_enforcement_state(datetime.now() + timedelta(minutes=10))
        state = json.loads(self.enforcer.state_file.read_text())
        state['blocked_sites'] = ['example.com\n10.0.0.1 unrelated.example']
        self.enforcer.state_file.write_text(json.dumps(state))
        original = self.hosts.read_text()
        self.assertIsNone(self.enforcer.recover_enforcement())
        self.assertIn('Could not restore blocking rules', self.enforcer.last_error)
        self.assertEqual(self.hosts.read_text(), original)

    def test_expired_block_cleanup_does_not_depend_on_saved_rules(self):
        self.enforcer.modify_hosts_file(True)
        self.enforcer.save_enforcement_state(datetime.now() - timedelta(minutes=1))
        state = json.loads(self.enforcer.state_file.read_text())
        state['blocked_apps'] = None
        self.enforcer.state_file.write_text(json.dumps(state))
        self.assertIsNone(self.enforcer.recover_enforcement())
        self.assertFalse(self.enforcer.has_block_entries())


if __name__ == "__main__":
    unittest.main()
