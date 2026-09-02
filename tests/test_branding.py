import unittest
from pathlib import Path


class TestFocoBranding(unittest.TestCase):
    def test_user_facing_files_use_the_foco_name(self):
        root = Path(__file__).resolve().parents[1]
        files = [
            'README.md', 'main.py', 'app_launcher.py', 'dashboard.py', 'install.py',
            'setup_app.py', 'run_as_admin.bat', 'start_focus_jail.bat',
            'create_manifest.py', 'youtube_filter.py',
        ]
        legacy_names = [('AD' + 'HD'), ('Productivity ' + 'Tracker')]
        combined = '\n'.join((root / name).read_text(encoding='utf-8') for name in files)

        self.assertIn('Foco', combined)
        for legacy_name in legacy_names:
            self.assertNotIn(legacy_name, combined)


if __name__ == '__main__':
    unittest.main()
