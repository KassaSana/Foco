"""Activities tab UI and editable timeline actions."""

from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk


class ActivitiesTab:
    def _build_activities_tab(self):
        frame = ttk.Frame(self.activities_tab)
        frame.pack(fill="both", expand=True, padx=14, pady=12)

        header = ttk.Frame(frame)
        header.pack(fill="x")
        ttk.Label(header, text="Activities", font=("Segoe UI", 14, "bold")).pack(
            side="left"
        )
        buttons = ttk.Frame(header)
        buttons.pack(side="right")
        ttk.Button(buttons, text="Add", command=self._add_activity).pack(
            side="left", padx=4
        )
        ttk.Button(buttons, text="Delete", command=self._delete_activity).pack(
            side="left", padx=4
        )
        ttk.Button(buttons, text="Save", command=self._save_activities).pack(
            side="left", padx=4
        )

        columns = ("start", "end", "label", "category", "duration")
        self.activities_tree = ttk.Treeview(
            frame, columns=columns, show="headings", height=18
        )
        for column in columns:
            self.activities_tree.heading(column, text=column.title())
            self.activities_tree.column(
                column, width=130 if column != "label" else 220
            )
        self.activities_tree.pack(fill="both", expand=True, pady=8)
        self.activities_tree.bind("<Double-1>", self._edit_cell)
        self._editing_activity = None
        ttk.Label(
            frame,
            text="Double-click a cell to edit. Auto-logged items appear here.",
            font=("Segoe UI", 9),
        ).pack(anchor="w")

    def _add_activity(self):
        now = datetime.now().strftime("%H:%M")
        self.activities_tree.insert(
            "", "end", values=(now, "", "New Item", "Uncategorized", "")
        )

    def _delete_activity(self):
        for selection in self.activities_tree.selection():
            self.activities_tree.delete(selection)

    def _save_activities(self):
        rows = []
        for item_id in self.activities_tree.get_children():
            values = self.activities_tree.item(item_id)["values"]
            rows.append(
                {
                    "start_time": values[0],
                    "end_time": values[1],
                    "label": values[2],
                    "category": values[3],
                    "duration_minutes": values[4],
                }
            )
        try:
            self.data_logger.replace_activities(rows)
            self._refresh_activities()
        except Exception as error:
            messagebox.showerror("Save Failed", str(error))

    def _edit_cell(self, event):
        region = self.activities_tree.identify("region", event.x, event.y)
        if region != "cell":
            return
        row_id = self.activities_tree.identify_row(event.y)
        column_id = self.activities_tree.identify_column(event.x)
        if not row_id or not column_id:
            return
        column_index = int(column_id[1:]) - 1
        x, y, width, height = self.activities_tree.bbox(row_id, column_id)
        old_value = self.activities_tree.item(row_id)["values"][column_index]
        entry = tk.Entry(self.activities_tree)
        entry.place(x=x, y=y, width=width, height=height)
        entry.insert(0, old_value)
        entry.focus()
        self._editing_activity = (row_id, column_index, entry)

        def finish(_=None):
            values = list(self.activities_tree.item(row_id)["values"])
            values[column_index] = entry.get()
            self.activities_tree.item(row_id, values=values)
            entry.destroy()
            self._editing_activity = None

        entry.bind("<Return>", finish)
        entry.bind("<FocusOut>", finish)

    def _refresh_activities(self):
        if getattr(self, "_editing_activity", None) is not None:
            return
        try:
            activities = self.data_logger.get_recent_activities(limit=50)
        except Exception:
            activities = []
        self.activities_tree.delete(*self.activities_tree.get_children())
        for activity in activities:
            self.activities_tree.insert(
                "",
                "end",
                values=(
                    activity.get("start_time", ""),
                    activity.get("end_time", ""),
                    activity.get("label", activity.get("application", "")),
                    activity.get("category", ""),
                    activity.get("duration_minutes", ""),
                ),
            )
