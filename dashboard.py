"""
Dashboard - Tabbed Productivity Interface
Focus | Activities | Statistics
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from stats_calculator import StatsCalculator
from trend_analyzer import TrendAnalyzer
from focus_manager import FocusManager, FocusMode

class ProductivityDashboard:
    def __init__(self, root, data_logger, activity_monitor):
        self.root = root
        self.data_logger = data_logger
        self.activity_monitor = activity_monitor
        self.stats_calculator = StatsCalculator(data_logger)
        self.trend_analyzer = TrendAnalyzer(self.stats_calculator)
        self.focus_manager = FocusManager(data_logger)

        # State
        self.current_view = "Today"  # For statistics range selection
        self.view_date = datetime.now()
        self._manual_jail_active = False
        self.cached_stats = {}
        self.last_activity_text = ""

        self._build_ui()
        self._start_refresh_loop()

    # ---------------- UI Construction ----------------
    def _build_ui(self):
        self.root.title("ADHD Productivity Tracker")
        self.root.configure(bg="#2b2b2b")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=8, pady=8)

        self.focus_tab = ttk.Frame(self.notebook)
        self.activities_tab = ttk.Frame(self.notebook)
        self.stats_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.focus_tab, text="Focus")
        self.notebook.add(self.activities_tab, text="Activities")
        self.notebook.add(self.stats_tab, text="Statistics")

        self._build_focus_tab()
        self._build_activities_tab()
        self._build_stats_tab()

    # ---------------- Focus Tab ----------------
    def _build_focus_tab(self):
        f = ttk.Frame(self.focus_tab)
        f.pack(fill="both", expand=True, padx=14, pady=12)

        # Current Activity
        self.current_activity_label = ttk.Label(f, text="Current Activity: —", font=("Segoe UI", 11))
        self.current_activity_label.pack(anchor="w", pady=(0, 8))

        # Mode Selection
        mode_box = ttk.LabelFrame(f, text="Choose Focus Mode")
        mode_box.pack(fill="x", pady=4)
        self.mode_var = tk.StringVar(value="quick")
        ttk.Radiobutton(mode_box, text="Pomodoro (25 min)", value="quick", variable=self.mode_var).pack(side="left", padx=10, pady=6)
        ttk.Radiobutton(mode_box, text="Deep Work (90 min)", value="deep", variable=self.mode_var).pack(side="left", padx=10, pady=6)

        # Control Buttons
        btn_row = ttk.Frame(f)
        btn_row.pack(fill="x", pady=10)
        self.start_btn = ttk.Button(btn_row, text="Start Focus Session", command=self._start_focus)
        self.start_btn.pack(side="left")
        self.stop_btn = ttk.Button(btn_row, text="Stop Session", command=self._stop_focus, state="disabled")
        self.stop_btn.pack(side="left", padx=10)

        # Timer
        self.timer_label = ttk.Label(f, text="00:00", font=("Consolas", 36, "bold"), foreground="#4CAF50")
        self.timer_label.pack(pady=10)

        # Session Status
        self.session_status_label = ttk.Label(f, text="No active session", font=("Segoe UI", 10))
        self.session_status_label.pack()

        # Progress bar
        self.focus_progress = ttk.Progressbar(f, length=460, mode='determinate')
        self.focus_progress.pack(pady=12)

        # Jail status
        self.jail_status_label = ttk.Label(f, text="Productivity jail inactive", font=("Segoe UI", 10))
        self.jail_status_label.pack(pady=(4, 10))

        # Manual Jail Controls
        jail_frame = ttk.LabelFrame(f, text="Productivity Jail")
        jail_frame.pack(fill="x", pady=6)
        ttk.Button(jail_frame, text="🔒 2h", command=lambda: self._start_manual_jail(2)).pack(side="left", padx=4, pady=6)
        ttk.Button(jail_frame, text="🔒 4h", command=lambda: self._start_manual_jail(4)).pack(side="left", padx=4)
        ttk.Button(jail_frame, text="🔒 8h", command=lambda: self._start_manual_jail(8)).pack(side="left", padx=4)
        ttk.Button(jail_frame, text="🚨 Disable", command=self._disable_all_jail).pack(side="left", padx=16)

    def _start_focus(self):
        mode = self.mode_var.get()
        if mode == 'deep':
            self.focus_manager.start_focus_session(FocusMode.DEEP_WORK)
        else:
            self.focus_manager.start_focus_session(FocusMode.QUICK_FOCUS)
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')

    def _stop_focus(self):
        self.focus_manager.end_current_session()
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.timer_label.config(text="00:00", foreground="#4CAF50")
        self.session_status_label.config(text="No active session")
        if not self._manual_jail_active:
            self.jail_status_label.config(text="Productivity jail inactive")

    def _start_manual_jail(self, hours):
        try:
            from productivity_enforcer import ProductivityEnforcer
            import tkinter.messagebox as m
            if not m.askyesno("Start Jail", f"Start {hours}h distraction block?"):
                return
            self.manual_jail = ProductivityEnforcer()
            if self.manual_jail.start_enforcement(hours):
                self._manual_jail_active = True
                self.jail_status_label.config(text=f"🔒 Manual jail active ({hours}h)")
        except Exception as e:
            import tkinter.messagebox as m
            m.showerror("Error", f"Failed to start jail: {e}")

    def _disable_all_jail(self):
        try:
            from productivity_enforcer import ProductivityEnforcer
            import tkinter.messagebox as m
            if not m.askyesno("Disable", "Disable all blocking?"):
                return
            if hasattr(self.focus_manager, 'jail_enforcer'):
                self.focus_manager._stop_jail_mode()
            if hasattr(self, 'manual_jail'):
                self.manual_jail.stop_enforcement()
            ProductivityEnforcer().stop_enforcement()
            self._manual_jail_active = False
            self.jail_status_label.config(text="Productivity jail inactive")
        except Exception as e:
            import tkinter.messagebox as m
            m.showerror("Error", f"Disable failed: {e}")

    # ---------------- Activities Tab ----------------
    def _build_activities_tab(self):
        f = ttk.Frame(self.activities_tab)
        f.pack(fill="both", expand=True, padx=14, pady=12)

        header = ttk.Frame(f)
        header.pack(fill="x")
        ttk.Label(header, text="Activities", font=("Segoe UI", 14, "bold")).pack(side="left")
        btns = ttk.Frame(header)
        btns.pack(side="right")
        ttk.Button(btns, text="Add", command=self._add_activity).pack(side="left", padx=4)
        ttk.Button(btns, text="Delete", command=self._delete_activity).pack(side="left", padx=4)
        ttk.Button(btns, text="Save", command=self._save_activities).pack(side="left", padx=4)

        cols = ("start", "end", "label", "category", "duration")
        self.activities_tree = ttk.Treeview(f, columns=cols, show='headings', height=18)
        for c in cols:
            self.activities_tree.heading(c, text=c.title())
            self.activities_tree.column(c, width=130 if c != 'label' else 220)
        self.activities_tree.pack(fill='both', expand=True, pady=8)
        self.activities_tree.bind('<Double-1>', self._edit_cell)
        # Track active edit to avoid refresh collisions
        self._editing_activity = None  # track editing state

        ttk.Label(f, text="Double-click a cell to edit. Auto-logged items appear here.", font=("Segoe UI", 9)).pack(anchor='w')

    def _add_activity(self):
        now = datetime.now().strftime('%H:%M')
        self.activities_tree.insert('', 'end', values=(now, '', 'New Item', 'Uncategorized', ''))

    def _delete_activity(self):
        for sel in self.activities_tree.selection():
            self.activities_tree.delete(sel)

    def _save_activities(self):
        rows = []
        for iid in self.activities_tree.get_children():
            vals = self.activities_tree.item(iid)['values']
            rows.append({
                'start_time': vals[0], 'end_time': vals[1], 'label': vals[2],
                'category': vals[3], 'duration_minutes': vals[4]
            })
        if hasattr(self.data_logger, 'save_activity_overrides'):
            try:
                self.data_logger.save_activity_overrides(rows)
            except Exception as e:
                import tkinter.messagebox as m
                m.showerror("Save Failed", str(e))

    def _edit_cell(self, event):
        region = self.activities_tree.identify('region', event.x, event.y)
        if region != 'cell':
            return
        row_id = self.activities_tree.identify_row(event.y)
        col_id = self.activities_tree.identify_column(event.x)
        if not row_id or not col_id:
            return
        col_index = int(col_id[1:]) - 1
        x, y, w, h = self.activities_tree.bbox(row_id, col_id)
        old = self.activities_tree.item(row_id)['values'][col_index]
        entry = tk.Entry(self.activities_tree)
        entry.place(x=x, y=y, width=w, height=h)
        entry.insert(0, old)
        entry.focus()
        self._editing_activity = (row_id, col_index, entry)
        def finish(_=None):
            new_val = entry.get()
            vals = list(self.activities_tree.item(row_id)['values'])
            vals[col_index] = new_val
            self.activities_tree.item(row_id, values=vals)
            entry.destroy()
            self._editing_activity = None
        entry.bind('<Return>', finish)
        entry.bind('<FocusOut>', finish)

    def _refresh_activities(self):
        # Avoid refreshing while editing to prevent item-not-found errors
        if getattr(self, '_editing_activity', None) is not None:
            return
        if hasattr(self.data_logger, 'get_recent_activities'):
            try:
                acts = self.data_logger.get_recent_activities(limit=50)
            except Exception:
                acts = []
        else:
            acts = []
        self.activities_tree.delete(*self.activities_tree.get_children())
        for a in acts:
            self.activities_tree.insert('', 'end', values=(
                a.get('start_time', ''),
                a.get('end_time', ''),
                a.get('label', a.get('application', '')),
                a.get('category', ''),
                a.get('duration_minutes', '')
            ))

    # ---------------- Statistics Tab ----------------
    def _build_stats_tab(self):
        f = ttk.Frame(self.stats_tab)
        f.pack(fill='both', expand=True, padx=14, pady=12)

        top = ttk.Frame(f)
        top.pack(fill='x')
        ttk.Label(top, text="Statistics", font=("Segoe UI", 14, 'bold')).pack(side='left')

        self.range_var = tk.StringVar(value='Today')
        rng = ttk.Frame(top)
        rng.pack(side='right')
        for label in ['Today', 'This Week', 'This Month', 'This Year']:
            ttk.Radiobutton(rng, text=label, value=label, variable=self.range_var, command=self._update_stats).pack(side='left', padx=4)

        self.stats_container = ttk.Frame(f)
        self.stats_container.pack(fill='both', expand=True, pady=10)

    def _update_stats(self):
        for w in self.stats_container.winfo_children():
            w.destroy()
        view = self.range_var.get()
        try:
            if view == 'Today':
                stats = self.data_logger.get_today_summary()
                self._render_daily_stats(stats)
            elif view == 'This Week':
                monday = datetime.now() - timedelta(days=datetime.now().weekday())
                stats = self.stats_calculator.calculate_weekly_stats(monday)
                self._render_weekly_stats(stats)
            elif view == 'This Month':
                now = datetime.now()
                stats = self.stats_calculator.calculate_monthly_stats(now.year, now.month)
                self._render_monthly_stats(stats)
            else:
                now = datetime.now()
                stats = self.stats_calculator.calculate_yearly_stats(now.year)
                self._render_yearly_stats(stats)
        except Exception as e:
            ttk.Label(self.stats_container, text=f"Stats error: {e}").pack(anchor='w')

    # --- Render helpers ---
    def _render_daily_stats(self, stats):
        total_hours = stats['total_productive'] / 60 if stats.get('total_productive') else 0
        header = ttk.Label(self.stats_container, text=f"Real Work: {total_hours:.1f}h | Switches: {stats.get('context_switches',0)}", font=("Segoe UI", 11, 'bold'))
        header.pack(anchor='w', pady=(0,6))
        rows = [
            ('Building', stats.get('building',0), '#4CAF50'),
            ('Studying', stats.get('studying',0), '#2196F3'),
            ('Applying', stats.get('applying',0), '#FF9800'),
            ('Knowledge', stats.get('knowledge',0), '#9C27B0'),
        ]
        for label, minutes, color in rows:
            self._category_row(label, minutes, stats.get('total_productive',1), color)

    def _render_weekly_stats(self, stats):
        ttk.Label(self.stats_container, text=f"Week Total: {stats['totals']['total_productive']/60:.1f}h", font=("Segoe UI",11,'bold')).pack(anchor='w')
        max_hours = max((d['total'] for d in stats['daily_summaries']), default=1)/60
        for name, day in zip(['Mon','Tue','Wed','Thu','Fri','Sat','Sun'], stats['daily_summaries']):
            self._day_bar(name, day['total']/60, max_hours)

    def _render_monthly_stats(self, stats):
        ttk.Label(self.stats_container, text=f"Month Total: {stats['totals']['total_productive']/60:.1f}h", font=("Segoe UI",11,'bold')).pack(anchor='w')
        rows = [
            ('Building', stats['totals']['building'], '#4CAF50'),
            ('Studying', stats['totals']['studying'], '#2196F3'),
            ('Applying', stats['totals']['applying'], '#FF9800'),
            ('Knowledge', stats['totals']['knowledge'], '#9C27B0'),
        ]
        total = stats['totals']['total_productive'] or 1
        for label, minutes, color in rows:
            self._category_row(label, minutes, total, color)

    def _render_yearly_stats(self, stats):
        ttk.Label(self.stats_container, text=f"Year Total: {stats['totals']['total_productive']/60:.0f}h", font=("Segoe UI",11,'bold')).pack(anchor='w')
        max_h = max(stats['quarterly_summaries'], default=1)
        for q_label, hours in zip(['Q1','Q2','Q3','Q4'], stats['quarterly_summaries']):
            self._quarter_bar(q_label, hours, max_h)

    # --- Visual helpers ---
    def _category_row(self, label, minutes, total_minutes, color):
        row = ttk.Frame(self.stats_container)
        row.pack(fill='x', pady=2)
        ttk.Label(row, text=f"{label}: {minutes/60:.1f}h", width=18).pack(side='left')
        bar_bg = tk.Frame(row, bg='#444', height=18)
        bar_bg.pack(side='left', fill='x', expand=True, padx=6)
        if minutes > 0 and total_minutes > 0:
            tk.Frame(bar_bg, bg=color, height=18, width=int((minutes/total_minutes)*bar_bg.winfo_reqwidth())).place(relwidth=(minutes/total_minutes))

    def _day_bar(self, day, hours, max_hours):
        row = ttk.Frame(self.stats_container)
        row.pack(fill='x', pady=1)
        ttk.Label(row, text=f"{day}", width=4).pack(side='left')
        bar_bg = tk.Frame(row, bg='#444', height=18)
        bar_bg.pack(side='left', fill='x', expand=True, padx=4)
        if hours>0 and max_hours>0:
            tk.Frame(bar_bg, bg='#4CAF50', height=18).place(relwidth=hours/max_hours)
        ttk.Label(row, text=f"{hours:.1f}h", width=6).pack(side='right')

    def _quarter_bar(self, quarter, hours, max_hours):
        row = ttk.Frame(self.stats_container)
        row.pack(fill='x', pady=2)
        ttk.Label(row, text=quarter, width=4).pack(side='left')
        bar_bg = tk.Frame(row, bg='#444', height=22)
        bar_bg.pack(side='left', fill='x', expand=True, padx=6)
        if hours>0 and max_hours>0:
            tk.Frame(bar_bg, bg='#4CAF50', height=22).place(relwidth=hours/max_hours)
        ttk.Label(row, text=f"{hours:.0f}h", width=6).pack(side='right')

    # ---------------- Refresh Logic ----------------
    def _start_refresh_loop(self):
        self._update_focus()
        self._update_activity()
        self._update_stats()
        self.root.after(2000, self._start_refresh_loop)

    def _update_focus(self):
        info = self.focus_manager.get_session_info()
        if info:
            remaining = info['remaining_minutes'] * 60
            time_text = self.focus_manager.format_time(remaining)
            self.timer_label.config(text=time_text, foreground="#4CAF50" if remaining>300 else "#FF9800")
            self.session_status_label.config(text=f"{info['mode']} - {info['state']} ({info['progress_percentage']:.0f}%)")
            # Progress
            pct = info['progress_percentage']
            self.focus_progress['value'] = pct
            # Jail indicator
            if info['mode'] == 'Deep Work' and self.focus_manager.session_data.get('jail_active'):
                self.jail_status_label.config(text='🔒 Auto jail active (Deep Work)')
            elif not self._manual_jail_active:
                self.jail_status_label.config(text='Productivity jail inactive')
        else:
            self.focus_progress['value'] = 0

    def _update_activity(self):
        current = self.activity_monitor.get_current_activity()
        if current:
            app = current.get('application') or current.get('window_title','App')
            category = current.get('category','')
            txt = f"Current Activity: {app}  |  {category}"
        else:
            txt = "Current Activity: —"
        if txt != self.last_activity_text:
            self.current_activity_label.config(text=txt)
            self.last_activity_text = txt
        # Refresh activities tree occasionally
        if self.notebook.index(self.notebook.select()) == 1:  # Activities tab visible
            self._refresh_activities()

    # Public alias for external triggers if needed
    def refresh_now(self):
        self._update_stats()

# End of refactored dashboard