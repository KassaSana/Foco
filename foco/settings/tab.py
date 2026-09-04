"""Settings tab UI and configuration editing."""

import tkinter as tk
from tkinter import messagebox, ttk

from ..config import load_config, save_config


class SettingsTab:
    def _build_settings_tab(self):
        container = ttk.Frame(self.settings_tab)
        container.pack(fill="both", expand=True, padx=14, pady=12)
        heading = ttk.Frame(container)
        heading.pack(fill="x")
        ttk.Label(heading, text="Settings", font=("Segoe UI", 14, "bold")).pack(
            side="left"
        )
        ttk.Button(
            heading, text="Save Settings", command=self._save_settings
        ).pack(side="right")

        timing = ttk.LabelFrame(container, text="Timing and limits")
        timing.pack(fill="x", pady=(10, 8))
        self.deep_minutes_var = tk.StringVar()
        self.quick_minutes_var = tk.StringVar()
        self.idle_minutes_var = tk.StringVar()
        self.pseudo_limit_var = tk.StringVar()
        for column, (label, variable) in enumerate(
            (
                ("Deep Work (min)", self.deep_minutes_var),
                ("Quick Focus (min)", self.quick_minutes_var),
                ("Idle timeout (min)", self.idle_minutes_var),
                ("Distraction budget (0=off)", self.pseudo_limit_var),
            )
        ):
            ttk.Label(timing, text=label).grid(
                row=0, column=column, padx=8, pady=(6, 2), sticky="w"
            )
            ttk.Entry(timing, textvariable=variable, width=18).grid(
                row=1, column=column, padx=8, pady=(0, 8), sticky="w"
            )

        rules = ttk.Notebook(container)
        rules.pack(fill="both", expand=True)
        classification = ttk.Frame(rules)
        blocking = ttk.Frame(rules)
        rules.add(classification, text="Classification Rules")
        rules.add(blocking, text="Blocking Rules")
        self.settings_texts = {}
        self._add_rule_editor(
            classification, "Building app/process patterns", "building_apps", 0
        )
        self._add_rule_editor(
            classification, "Studying app/title patterns", "studying_apps", 1
        )
        self._add_rule_editor(
            classification, "Applying site/title patterns", "applying_sites", 2
        )
        self._add_rule_editor(
            classification,
            "Pseudo-productive site/title patterns",
            "pseudo_productive_sites",
            3,
        )
        self._add_rule_editor(
            blocking, "Blocked domains", "blocked_sites", 0, height=8
        )
        self._add_rule_editor(
            blocking, "Blocked executable names", "blocked_apps", 1, height=8
        )
        ttk.Label(
            container,
            text="Enter one rule per line. Blocking changes apply when the next jail starts.",
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(6, 0))
        self._load_settings_form()

    def _add_rule_editor(self, parent, label, key, row, height=3):
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, sticky="nsew", padx=8, pady=5)
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(row, weight=1)
        ttk.Label(frame, text=label).pack(anchor="w")
        editor = tk.Text(frame, height=height, wrap="word")
        editor.pack(fill="both", expand=True)
        self.settings_texts[key] = editor

    def _load_settings_form(self):
        config = load_config(self.runtime_paths.config_file)
        self.deep_minutes_var.set(str(config["focus_modes"]["deep_work"]))
        self.quick_minutes_var.set(str(config["focus_modes"]["quick_focus"]))
        self.idle_minutes_var.set(str(config["idle_timeout"]))
        self.pseudo_limit_var.set(str(config["pseudo_productive_limit"]))
        for key, editor in self.settings_texts.items():
            editor.delete("1.0", "end")
            editor.insert("1.0", "\n".join(config[key]))

    def _save_settings(self):
        try:
            config = load_config(self.runtime_paths.config_file)
            config["focus_modes"] = {
                "deep_work": int(self.deep_minutes_var.get()),
                "quick_focus": int(self.quick_minutes_var.get()),
            }
            config["idle_timeout"] = float(self.idle_minutes_var.get())
            config["pseudo_productive_limit"] = float(self.pseudo_limit_var.get())
            for key, editor in self.settings_texts.items():
                values = []
                for line in editor.get("1.0", "end").splitlines():
                    values.extend(
                        part.strip() for part in line.split(",") if part.strip()
                    )
                config[key] = values
            config = save_config(config, self.runtime_paths.config_file)
            self.activity_monitor.category_engine.reload_config()
            self.activity_monitor.idle_threshold = config["idle_timeout"] * 60
            self.focus_manager.reload_config()
            self.distraction_budget.reload_config()
            self._load_settings_form()
            messagebox.showinfo(
                "Settings saved",
                "New tracking and focus sessions will use these rules.",
            )
        except (ValueError, OSError) as error:
            messagebox.showerror("Invalid settings", str(error))
