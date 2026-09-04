"""Smoke tests for the application entry point."""

import importlib
import unittest


class TestApplicationEntrypoint(unittest.TestCase):
    def test_application_entrypoint_imports_without_starting_the_gui(self):
        app = importlib.import_module("foco.app")

        self.assertTrue(callable(app.main))
        self.assertTrue(hasattr(app, "FocoApp"))


if __name__ == "__main__":
    unittest.main()
