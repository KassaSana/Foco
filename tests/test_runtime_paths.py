import tempfile
import unittest
from pathlib import Path

from foco.runtime_paths import prepare_runtime_paths


class TestRuntimePaths(unittest.TestCase):
    def test_source_run_uses_repository_root(self):
        paths = prepare_runtime_paths(frozen=False)
        repository_root = Path(__file__).resolve().parents[1]

        self.assertEqual(paths.config_file, repository_root / "config.json")
        self.assertEqual(paths.data_dir, repository_root / "productivity_data")

    def test_packaged_run_seeds_stable_user_configuration(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            bundle_dir = root / "bundle"
            local_app_data = root / "local"
            bundle_dir.mkdir()
            bundled_config = bundle_dir / "config.json"
            bundled_config.write_text('{"idle_timeout": 7}\n', encoding="utf-8")

            paths = prepare_runtime_paths(
                frozen=True,
                bundle_dir=bundle_dir,
                local_app_data=local_app_data,
            )

            self.assertEqual(paths.config_file, local_app_data / "Foco" / "config.json")
            self.assertEqual(
                paths.data_dir, local_app_data / "Foco" / "productivity_data"
            )
            self.assertEqual(paths.config_file.read_bytes(), bundled_config.read_bytes())

    def test_existing_packaged_configuration_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            bundle_dir = root / "bundle"
            user_root = root / "local" / "Foco"
            bundle_dir.mkdir()
            user_root.mkdir(parents=True)
            (bundle_dir / "config.json").write_text("bundled", encoding="utf-8")
            user_config = user_root / "config.json"
            user_config.write_text("user settings", encoding="utf-8")

            paths = prepare_runtime_paths(
                frozen=True,
                bundle_dir=bundle_dir,
                local_app_data=root / "local",
            )

            self.assertEqual(paths.config_file.read_text(encoding="utf-8"), "user settings")


if __name__ == "__main__":
    unittest.main()
