"""Threshold logic for the daily distraction budget."""

from ..config import load_config


class DistractionBudget:
    def __init__(self, data_logger, config_path="config.json"):
        self.data_logger = data_logger
        self.config_path = config_path
        self.reload_config()

    def reload_config(self):
        """Apply the saved limit to future status checks."""
        self.limit_minutes = float(
            load_config(self.config_path)["pseudo_productive_limit"]
        )

    def get_status(self, active_pseudo_minutes=0):
        """Return today's usage, including a currently active pseudo segment."""
        summary = self.data_logger.get_today_summary()
        state = self.data_logger.get_distraction_budget_state()
        try:
            active_minutes = max(0, float(active_pseudo_minutes or 0))
        except (TypeError, ValueError):
            active_minutes = 0
        used_minutes = max(
            0, float(summary.get("pseudo_productive", 0) or 0)
        ) + active_minutes
        enabled = self.limit_minutes > 0
        crossed = enabled and used_minutes >= self.limit_minutes
        alerted = bool(state.get("alerted", False))
        progress = (
            min(100, (used_minutes / self.limit_minutes) * 100)
            if enabled
            else 0
        )
        return {
            "used_minutes": round(used_minutes, 1),
            "limit_minutes": self.limit_minutes,
            "enabled": enabled,
            "crossed": crossed,
            "alerted": alerted,
            "should_alert": crossed and not alerted,
            "progress_percentage": round(progress, 1),
        }

    def acknowledge_alert(self):
        """Persist that today's threshold notification has been shown."""
        self.data_logger.mark_distraction_budget_alerted()
