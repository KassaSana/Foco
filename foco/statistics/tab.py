"""Statistics tab UI and range-specific rendering."""

from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk


class StatisticsTab:
    def _build_stats_tab(self):
        frame = ttk.Frame(self.stats_tab)
        frame.pack(fill="both", expand=True, padx=14, pady=12)
        top = ttk.Frame(frame)
        top.pack(fill="x")
        ttk.Label(top, text="Statistics", font=("Segoe UI", 14, "bold")).pack(
            side="left"
        )
        self.range_var = tk.StringVar(value="Today")
        range_frame = ttk.Frame(top)
        range_frame.pack(side="right")
        for label in ["Today", "This Week", "This Month", "This Year"]:
            ttk.Radiobutton(
                range_frame,
                text=label,
                value=label,
                variable=self.range_var,
                command=self._update_stats,
            ).pack(side="left", padx=4)
        self.stats_container = ttk.Frame(frame)
        self.stats_container.pack(fill="both", expand=True, pady=10)

    def _update_stats(self):
        for widget in self.stats_container.winfo_children():
            widget.destroy()
        view = self.range_var.get()
        try:
            if view == "Today":
                self._render_daily_stats(self.stats_calculator.calculate_daily_stats())
            elif view == "This Week":
                monday = datetime.now() - timedelta(days=datetime.now().weekday())
                self._render_weekly_stats(
                    self.stats_calculator.calculate_weekly_stats(monday)
                )
            elif view == "This Month":
                now = datetime.now()
                self._render_monthly_stats(
                    self.stats_calculator.calculate_monthly_stats(now.year, now.month)
                )
            else:
                self._render_yearly_stats(
                    self.stats_calculator.calculate_yearly_stats(datetime.now().year)
                )
        except Exception as error:
            ttk.Label(self.stats_container, text=f"Stats error: {error}").pack(
                anchor="w"
            )

    def _render_daily_stats(self, stats):
        total_hours = stats.get("total_productive", 0) / 60
        ttk.Label(
            self.stats_container,
            text=(
                f"Real Work: {total_hours:.1f}h | "
                f"Switches: {stats.get('context_switches', 0)}"
            ),
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w", pady=(0, 6))
        rows = [
            ("Building", stats.get("building", 0), "#4CAF50"),
            ("Studying", stats.get("studying", 0), "#2196F3"),
            ("Applying", stats.get("applying", 0), "#FF9800"),
            ("Knowledge", stats.get("knowledge", 0), "#9C27B0"),
        ]
        for label, minutes, color in rows:
            self._category_row(
                label, minutes, stats.get("total_productive", 1), color
            )
        self._render_metrics(stats["metrics"])

    def _render_weekly_stats(self, stats):
        ttk.Label(
            self.stats_container,
            text=f"Week Total: {stats['totals']['total_productive'] / 60:.1f}h",
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w")
        max_hours = max(
            (day["total"] for day in stats["daily_summaries"]), default=1
        ) / 60
        for name, day in zip(
            ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            stats["daily_summaries"],
        ):
            self._day_bar(name, day["total"] / 60, max_hours)
        monday = datetime.now() - timedelta(days=datetime.now().weekday())
        previous = self.stats_calculator.calculate_weekly_stats(
            monday - timedelta(days=7)
        )
        current_minutes = stats["totals"]["total_productive"]
        previous_minutes = previous["totals"]["total_productive"]
        if previous_minutes:
            growth = ((current_minutes - previous_minutes) / previous_minutes) * 100
            direction = "up" if growth > 0 else "down" if growth < 0 else "stable"
            ttk.Label(
                self.stats_container,
                text=f"Week-over-week: {growth:+.1f}% ({direction})",
            ).pack(anchor="w", pady=(8, 0))
        self._render_metrics(stats["metrics"])

    def _render_monthly_stats(self, stats):
        ttk.Label(
            self.stats_container,
            text=f"Month Total: {stats['totals']['total_productive'] / 60:.1f}h",
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w")
        rows = [
            ("Building", stats["totals"]["building"], "#4CAF50"),
            ("Studying", stats["totals"]["studying"], "#2196F3"),
            ("Applying", stats["totals"]["applying"], "#FF9800"),
            ("Knowledge", stats["totals"]["knowledge"], "#9C27B0"),
        ]
        total = stats["totals"]["total_productive"] or 1
        for label, minutes, color in rows:
            self._category_row(label, minutes, total, color)
        self._render_metrics(stats["metrics"])

    def _render_yearly_stats(self, stats):
        ttk.Label(
            self.stats_container,
            text=f"Year Total: {stats['totals']['total_productive'] / 60:.0f}h",
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w")
        max_hours = max(stats["quarterly_summaries"], default=1)
        for quarter, hours in zip(
            ["Q1", "Q2", "Q3", "Q4"], stats["quarterly_summaries"]
        ):
            self._quarter_bar(quarter, hours, max_hours)
        self._render_metrics(stats["metrics"])

    def _render_metrics(self, metrics):
        panel = ttk.LabelFrame(self.stats_container, text="Focus quality")
        panel.pack(fill="x", pady=(12, 4))
        line = (
            f"Pseudo ratio: {metrics['pseudo_ratio']:.0f}%   |   "
            f"Focus completion: {metrics['focus_completion_rate']:.0f}%   |   "
            f"Focused: {metrics['focus_minutes'] / 60:.1f}h"
        )
        ttk.Label(panel, text=line, font=("Segoe UI", 10, "bold")).pack(
            anchor="w", padx=8, pady=(6, 2)
        )
        ttk.Label(
            panel,
            text=(
                f"Average work block: {metrics['average_work_block']:.0f}m   |   "
                f"Longest: {metrics['longest_work_block']:.0f}m"
            ),
        ).pack(anchor="w", padx=8, pady=(0, 4))
        for insight in self.stats_calculator.build_insights(metrics):
            ttk.Label(panel, text=f"• {insight}").pack(anchor="w", padx=8)
        ttk.Frame(panel, height=4).pack()

    def _category_row(self, label, minutes, total_minutes, color):
        row = ttk.Frame(self.stats_container)
        row.pack(fill="x", pady=2)
        ttk.Label(row, text=f"{label}: {minutes / 60:.1f}h", width=18).pack(
            side="left"
        )
        background = tk.Frame(row, bg="#444", height=18)
        background.pack(side="left", fill="x", expand=True, padx=6)
        if minutes > 0 and total_minutes > 0:
            tk.Frame(background, bg=color, height=18).place(
                relwidth=minutes / total_minutes
            )

    def _day_bar(self, day, hours, max_hours):
        row = ttk.Frame(self.stats_container)
        row.pack(fill="x", pady=1)
        ttk.Label(row, text=day, width=4).pack(side="left")
        background = tk.Frame(row, bg="#444", height=18)
        background.pack(side="left", fill="x", expand=True, padx=4)
        if hours > 0 and max_hours > 0:
            tk.Frame(background, bg="#4CAF50", height=18).place(
                relwidth=hours / max_hours
            )
        ttk.Label(row, text=f"{hours:.1f}h", width=6).pack(side="right")

    def _quarter_bar(self, quarter, hours, max_hours):
        row = ttk.Frame(self.stats_container)
        row.pack(fill="x", pady=2)
        ttk.Label(row, text=quarter, width=4).pack(side="left")
        background = tk.Frame(row, bg="#444", height=22)
        background.pack(side="left", fill="x", expand=True, padx=6)
        if hours > 0 and max_hours > 0:
            tk.Frame(background, bg="#4CAF50", height=22).place(
                relwidth=hours / max_hours
            )
        ttk.Label(row, text=f"{hours:.0f}h", width=6).pack(side="right")
