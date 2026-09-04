"""Activities tab UI and editable timeline actions."""

from datetime import datetime, timedelta
import math
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
        self.activity_date_var = tk.StringVar(value="Today")
        ttk.Button(header, text="Previous", command=lambda: self._change_activity_day(-1)).pack(
            side="right", padx=2
        )
        ttk.Button(header, text="Next", command=lambda: self._change_activity_day(1)).pack(
            side="right", padx=2
        )
        ttk.Label(header, textvariable=self.activity_date_var).pack(side="right", padx=8)
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
        ttk.Button(buttons, text="Cancel", command=self._cancel_activity_edits).pack(
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
        self._activities_dirty = False
        self._activity_records = {}
        self._activity_snapshot = None
        self.activity_edit_status = ttk.Label(
            frame,
            text="Double-click a cell to edit. Save changes or Cancel to discard them.",
            font=("Segoe UI", 9),
        )
        self.activity_edit_status.pack(anchor="w")
        self._refresh_activities()

    def _change_activity_day(self, days):
        if self._activities_dirty and not messagebox.askyesno(
            "Discard changes", "Discard unsaved activity changes?"
        ):
            return
        current = datetime.now() if self._activity_snapshot is None else datetime.strptime(
            self._activity_snapshot['date'], '%Y-%m-%d'
        )
        selected = current + timedelta(days=days)
        if selected.date() > datetime.now().date():
            return
        self._activities_dirty = False
        self._activity_date = selected.strftime('%Y-%m-%d')
        self.activity_date_var.set(self._activity_date)
        self._refresh_activities()

    def _mark_activities_dirty(self):
        self._activities_dirty = True
        self.activity_edit_status.config(text="Unsaved changes. Save or Cancel to resume live updates.")

    def _add_activity(self):
        self._finish_activity_edit()
        now = datetime.now().strftime("%H:%M")
        self.activities_tree.insert(
            "", "end", values=(now, "", "New Item", "Uncategorized", "")
        )
        self._mark_activities_dirty()

    def _delete_activity(self):
        self._finish_activity_edit()
        for selection in self.activities_tree.selection():
            self.activities_tree.delete(selection)
            self._mark_activities_dirty()

    def _save_activities(self):
        self._finish_activity_edit()
        if not self._activities_dirty:
            return
        try:
            rows = []
            for item_id in self.activities_tree.get_children():
                values = self.activities_tree.item(item_id)["values"]
                original = self._activity_records.get(item_id, {})
                record = original.copy()
                # Preserve the original record byte-for-byte for untouched rows.
                if tuple(map(str, values)) == tuple(map(str, self._activity_values(original))):
                    rows.append(record)
                    continue
                label = str(values[2]).strip()
                duration = float(values[4] or 0)
                if not label or not math.isfinite(duration) or duration < 0:
                    raise ValueError("Each activity needs a label and a finite, non-negative duration.")
                record.update(start_time=str(values[0]), end_time=str(values[1]),
                              duration_minutes=round(duration, 1))
                if label != str(self._activity_values(original)[2]):
                    record['activity'] = label
                category = str(values[3]).strip() or 'Uncategorized'
                if category != self._activity_values(original)[3]:
                    record['category'] = category
                    record['is_pseudo_productive'] = category.lower() == 'pseudo_productive'
                if not original:
                    record.update(application=label, window_title=label, source='manual',
                                  category=category,
                                  is_pseudo_productive=category.lower() == 'pseudo_productive')
                rows.append(record)
            self.data_logger.save_activity_edits(
                self._activity_snapshot['date'], self._activity_snapshot['sessions'], rows
            )
            self._activities_dirty = False
            self._refresh_activities()
        except Exception as error:
            messagebox.showerror("Save Failed", str(error))

    def _cancel_activity_edits(self):
        self._finish_activity_edit()
        if self._activities_dirty and not messagebox.askyesno(
            "Discard changes", "Discard unsaved activity changes?"
        ):
            return
        self._activities_dirty = False
        self._refresh_activities()

    @staticmethod
    def _activity_values(activity):
        return (
            activity.get('start_time') or activity.get('timestamp') or '',
            activity.get('end_time', ''),
            activity.get('activity') or activity.get('window_title')
            or activity.get('application') or 'Session',
            'Pseudo_productive' if activity.get('is_pseudo_productive')
            else activity.get('category', 'Uncategorized'),
            activity.get('duration_minutes', activity.get('duration', 0)),
        )

    def _finish_activity_edit(self, _=None):
        if self._editing_activity is None:
            return
        row_id, column_index, entry = self._editing_activity
        self._editing_activity = None
        values = list(self.activities_tree.item(row_id)['values'])
        value = entry.get()
        if str(values[column_index]) != value:
            values[column_index] = value
            self.activities_tree.item(row_id, values=values)
            self._mark_activities_dirty()
        entry.destroy()

    def _edit_cell(self, event):
        self._finish_activity_edit()
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

        entry.bind("<Return>", self._finish_activity_edit)
        entry.bind("<FocusOut>", self._finish_activity_edit)

    def _refresh_activities(self):
        if self._editing_activity is not None or self._activities_dirty:
            return
        try:
            snapshot = self.data_logger.get_day_data(getattr(self, '_activity_date', None))
        except Exception as error:
            self.activity_edit_status.config(text=f"Could not load activities: {error}")
            return
        self._activity_snapshot = snapshot
        self._activity_records = {}
        self.activities_tree.delete(*self.activities_tree.get_children())
        for activity in snapshot['sessions']:
            item_id = self.activities_tree.insert(
                "",
                "end",
                values=self._activity_values(activity),
            )
            self._activity_records[item_id] = activity
        self.activity_edit_status.config(
            text="Double-click a cell to edit. Save changes or Cancel to discard them."
        )
