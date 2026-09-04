"""Foco desktop application composition root."""

import threading
import time
import tkinter as tk
from tkinter import ttk

from .activities.tab import ActivitiesTab
from .activity_tracking.monitor import ActivityMonitor
from .focus.sessions import FocusManager
from .focus.tab import FocusTab
from .settings.tab import SettingsTab
from .statistics.calculator import StatsCalculator
from .statistics.tab import StatisticsTab
from .storage import DataLogger


class ProductivityDashboard(FocusTab, ActivitiesTab, StatisticsTab, SettingsTab):
    """Assemble the four feature-owned tabs into one desktop surface."""

    def __init__(self, root, data_logger, activity_monitor):
        self.root = root
        self.data_logger = data_logger
        self.activity_monitor = activity_monitor
        self.stats_calculator = StatsCalculator(data_logger)
        self.focus_manager = FocusManager(data_logger)
        self._manual_jail_active = False
        self.last_activity_text = ""

        self._build_ui()
        self._recover_jail()
        self._start_refresh_loop()

    def _build_ui(self):
        self.root.title("Foco")
        self.root.configure(bg="#2b2b2b")
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=8, pady=8)

        self.focus_tab = ttk.Frame(self.notebook)
        self.activities_tab = ttk.Frame(self.notebook)
        self.stats_tab = ttk.Frame(self.notebook)
        self.settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.focus_tab, text="Focus")
        self.notebook.add(self.activities_tab, text="Activities")
        self.notebook.add(self.stats_tab, text="Statistics")
        self.notebook.add(self.settings_tab, text="Settings")

        self._build_focus_tab()
        self._build_activities_tab()
        self._build_stats_tab()
        self._build_settings_tab()

    def _start_refresh_loop(self):
        self._update_focus()
        self._update_activity()
        self._update_stats()
        self.root.after(2000, self._start_refresh_loop)


class FocoApp:
    """Own the application window and activity-monitoring thread."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Foco")
        self.root.geometry("800x600")
        self.data_logger = DataLogger()
        self.activity_monitor = ActivityMonitor(self.data_logger)
        self.dashboard = ProductivityDashboard(
            self.root, self.data_logger, self.activity_monitor
        )
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self.start_monitoring, daemon=True
        )
        self.monitor_thread.start()

    def start_monitoring(self):
        """Run activity monitoring in the background."""
        while self.monitoring:
            self.activity_monitor.update()
            time.sleep(1)

    def run(self):
        """Start the GUI application."""
        try:
            self.root.mainloop()
        finally:
            self.monitoring = False
            self.monitor_thread.join(timeout=2)
            self.activity_monitor.stop()


def main():
    FocoApp().run()


if __name__ == "__main__":
    main()
