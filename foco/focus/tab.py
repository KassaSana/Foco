"""Focus tab UI and its user actions."""

from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk

from .blocker import ProductivityEnforcer
from .sessions import FocusManager, FocusMode


class FocusTab:
    def _build_focus_tab(self):
        f = ttk.Frame(self.focus_tab)
        f.pack(fill="both", expand=True, padx=14, pady=12)

        self.current_activity_label = ttk.Label(
            f, text="Current Activity: —", font=("Segoe UI", 11)
        )
        self.current_activity_label.pack(anchor="w", pady=(0, 8))

        budget_box = ttk.LabelFrame(f, text="Daily Distraction Budget")
        budget_box.pack(fill="x", pady=(0, 8))
        self.distraction_budget_label = ttk.Label(
            budget_box, text="Pseudo-productive time: 0 / 0 min"
        )
        self.distraction_budget_label.pack(anchor="w", padx=8, pady=(6, 2))
        self.distraction_budget_progress = ttk.Progressbar(
            budget_box, mode="determinate", maximum=100
        )
        self.distraction_budget_progress.pack(
            fill="x", padx=8, pady=(0, 6)
        )

        mode_box = ttk.LabelFrame(f, text="Choose Focus Mode")
        mode_box.pack(fill="x", pady=4)
        self.mode_var = tk.StringVar(value="quick")
        ttk.Radiobutton(
            mode_box, text="Pomodoro (25 min)", value="quick", variable=self.mode_var
        ).pack(side="left", padx=10, pady=6)
        ttk.Radiobutton(
            mode_box, text="Deep Work (90 min)", value="deep", variable=self.mode_var
        ).pack(side="left", padx=10, pady=6)

        btn_row = ttk.Frame(f)
        btn_row.pack(fill="x", pady=10)
        self.start_btn = ttk.Button(
            btn_row, text="Start Focus Session", command=self._start_focus
        )
        self.start_btn.pack(side="left")
        self.stop_btn = ttk.Button(
            btn_row, text="Stop Session", command=self._stop_focus, state="disabled"
        )
        self.stop_btn.pack(side="left", padx=10)
        self.pause_btn = ttk.Button(
            btn_row, text="Pause", command=self._toggle_pause, state="disabled"
        )
        self.pause_btn.pack(side="left")

        self.timer_label = ttk.Label(
            f, text="00:00", font=("Consolas", 36, "bold"), foreground="#4CAF50"
        )
        self.timer_label.pack(pady=10)
        self.session_status_label = ttk.Label(
            f, text="No active session", font=("Segoe UI", 10)
        )
        self.session_status_label.pack()
        self.focus_progress = ttk.Progressbar(f, length=460, mode="determinate")
        self.focus_progress.pack(pady=12)
        self.jail_status_label = ttk.Label(
            f, text="Productivity jail inactive", font=("Segoe UI", 10)
        )
        self.jail_status_label.pack(pady=(4, 10))

        jail_frame = ttk.LabelFrame(f, text="Productivity Jail")
        jail_frame.pack(fill="x", pady=6)
        ttk.Button(
            jail_frame, text="Block 2h", command=lambda: self._start_manual_jail(2)
        ).pack(side="left", padx=4, pady=6)
        ttk.Button(
            jail_frame, text="Block 4h", command=lambda: self._start_manual_jail(4)
        ).pack(side="left", padx=4)
        ttk.Button(
            jail_frame, text="Block 8h", command=lambda: self._start_manual_jail(8)
        ).pack(side="left", padx=4)
        ttk.Button(
            jail_frame, text="Disable", command=self._disable_all_jail
        ).pack(side="left", padx=16)

    def _start_focus(self):
        mode = self.mode_var.get()
        if mode == "deep":
            self.focus_manager.start_focus_session(FocusMode.DEEP_WORK)
        else:
            self.focus_manager.start_focus_session(FocusMode.QUICK_FOCUS)
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.pause_btn.config(state="normal", text="Pause")

    def _stop_focus(self):
        self.focus_manager.end_current_session()
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.pause_btn.config(state="disabled", text="Pause")
        self.timer_label.config(text="00:00", foreground="#4CAF50")
        self.session_status_label.config(text="No active session")
        if not self._manual_jail_active:
            self.jail_status_label.config(text="Productivity jail inactive")

    def _toggle_pause(self):
        if self.focus_manager.state.value == "Running":
            if self.focus_manager.pause_session():
                self.pause_btn.config(text="Resume")
        elif self.focus_manager.state.value == "Paused":
            if self.focus_manager.resume_session():
                self.pause_btn.config(text="Pause")

    def _start_manual_jail(self, hours):
        try:
            if not messagebox.askyesno(
                "Start Jail", f"Start {hours}h distraction block?"
            ):
                return
            self.manual_jail = ProductivityEnforcer(
                data_dir=self.runtime_paths.data_dir,
                config_path=self.runtime_paths.config_file,
            )
            if self.manual_jail.start_enforcement(hours):
                self._manual_jail_active = True
                self.manual_jail.start_monitoring()
                self.jail_status_label.config(text=f"Focus jail active ({hours}h)")
        except Exception as error:
            messagebox.showerror("Error", f"Failed to start jail: {error}")

    def _recover_jail(self):
        """Resume monitoring a saved jail or remove an expired stale block."""
        try:
            self.manual_jail = ProductivityEnforcer(
                data_dir=self.runtime_paths.data_dir,
                config_path=self.runtime_paths.config_file,
            )
            end_time = self.manual_jail.recover_enforcement()
            if end_time:
                self._manual_jail_active = True
                self.manual_jail.start_monitoring()
                remaining = max(
                    0, int((end_time - datetime.now()).total_seconds() / 60)
                )
                self.jail_status_label.config(
                    text=f"Focus jail restored ({remaining}m remaining)"
                )
        except Exception as error:
            print(f"Could not recover productivity jail: {error}")

    def _disable_all_jail(self):
        try:
            if not messagebox.askyesno("Disable", "Disable all blocking?"):
                return
            if hasattr(self.focus_manager, "jail_enforcer"):
                self.focus_manager._stop_jail_mode()
            if hasattr(self, "manual_jail"):
                self.manual_jail.stop_enforcement()
            ProductivityEnforcer(
                data_dir=self.runtime_paths.data_dir,
                config_path=self.runtime_paths.config_file,
            ).stop_enforcement()
            self._manual_jail_active = False
            self.jail_status_label.config(text="Productivity jail inactive")
        except Exception as error:
            messagebox.showerror("Error", f"Disable failed: {error}")

    def _update_focus(self):
        self.focus_manager.update()
        info = self.focus_manager.get_session_info()
        if info:
            remaining = info["remaining_seconds"]
            time_text = self.focus_manager.format_time(remaining)
            self.timer_label.config(
                text=time_text,
                foreground="#4CAF50" if remaining > 300 else "#FF9800",
            )
            self.session_status_label.config(
                text=(
                    f"{info['mode']} - {info['state']} "
                    f"({info['progress_percentage']:.0f}%)"
                )
            )
            self.focus_progress["value"] = info["progress_percentage"]
            if (
                info["mode"] == "Deep Work"
                and self.focus_manager.session_data.get("jail_active")
            ):
                self.jail_status_label.config(text="Focus jail active (Deep Work)")
            elif not self._manual_jail_active:
                self.jail_status_label.config(text="Productivity jail inactive")
            if info["state"] == "Completed":
                self.start_btn.config(state="normal")
                self.stop_btn.config(state="disabled")
                self.pause_btn.config(state="disabled", text="Pause")
        else:
            self.focus_progress["value"] = 0

    def _update_activity(self):
        current = self.activity_monitor.get_current_activity()
        if current:
            app = current.get("application") or current.get("window_title", "App")
            category = current.get("category", "")
            text = f"Current Activity: {app}  |  {category}"
        else:
            text = "Current Activity: —"
        if text != self.last_activity_text:
            self.current_activity_label.config(text=text)
            self.last_activity_text = text
        self._update_distraction_budget(current)
        if self.notebook.index(self.notebook.select()) == 1:
            self._refresh_activities()

    def _update_distraction_budget(self, current_activity):
        active_minutes = 0
        if current_activity and current_activity.get("is_pseudo_productive"):
            active_minutes = current_activity.get("duration", 0)
        status = self.distraction_budget.get_status(active_minutes)
        if not status["enabled"]:
            self.distraction_budget_label.config(
                text="Pseudo-productive time: alerts disabled"
            )
            self.distraction_budget_progress["value"] = 0
            return

        self.distraction_budget_label.config(
            text=(
                f"Pseudo-productive time: {status['used_minutes']:.1f} / "
                f"{status['limit_minutes']:g} min"
            )
        )
        self.distraction_budget_progress["value"] = status["progress_percentage"]
        if not status["should_alert"]:
            return

        self.distraction_budget.acknowledge_alert()
        if self.focus_manager.state.value in ("Running", "Paused"):
            messagebox.showinfo(
                "Distraction budget reached",
                "Today's distraction budget has been reached. "
                "Your focus session is already active.",
            )
            return
        if messagebox.askyesno(
            "Distraction budget reached",
            (
                f"You've used {status['used_minutes']:.1f} minutes of "
                "pseudo-productive time today. Start Quick Focus?"
            ),
        ):
            self.mode_var.set("quick")
            self._start_focus()
