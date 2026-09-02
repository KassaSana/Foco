import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from productivity_enforcer import ProductivityEnforcer


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


if __name__ == "__main__":
    unittest.main()
