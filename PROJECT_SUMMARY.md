# ADHD Productivity Tracker ("Trackkyyy") – Project Summary

## 1. Executive Elevator Pitch

An offline-first, Windows-focused ADHD productivity system that automatically distinguishes _real_ deep work from pseudo-productive thrashing. It tracks context switches, categorizes active application usage into meaningful learning/building modes, enforces distraction lockdown ("productivity jail") during 90‑minute Deep Work sessions, and surfaces multi-range statistics (daily / weekly / monthly / yearly) through a lightweight three‑tab desktop UI built with tkinter.

## 2. Core Value & Differentiators

- Automatic real‑time classification of activity (no manual time entries required).
- Distinguishes authentic productive states (Building / Studying / Applying / Knowledge) vs pseudo‑productive time.
- Integrated enforcement layer (web + app blocking) that auto‑activates for Deep Work; optional manual timed jail sessions (2h/4h/8h).
- Single‑user local JSON datastore (privacy preserving, portable, zero cloud dependency).
- Fast feedback loops: visual focus timer + progress + category distribution bars.
- Editable activity log with manual overrides while protecting in‑flight edits against refresh race conditions.

## 3. Quantitative Snapshot (Current Build)

| Dimension               | Metric (Approx.)            | Notes                                                                                                                                 |
| ----------------------- | --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| Total Python modules    | 15                          | Core + support scripts                                                                                                                |
| Primary feature modules | 7                           | focus_manager, productivity_enforcer, dashboard, activity_monitor, data_logger, stats_calculator, category_engine                     |
| Total Python LOC (est.) | ~1,350                      | Counted across representative core files (enforcer ~420, dashboard ~330, data_logger ~300, monitor ~190, focus_manager ~170 + others) |
| UI Tabs                 | 3                           | Focus / Activities / Statistics                                                                                                       |
| Focus Modes             | 2                           | 25m Quick Focus / 90m Deep Work                                                                                                       |
| Productivity Categories | 4 + pseudo flag             | building, studying, applying, knowledge (+ pseudo_productive)                                                                         |
| Blocking Coverage       | 40+ domains + 25+ processes | Social, entertainment, gaming, shopping, news                                                                                         |
| Background Threads      | 2                           | Focus/jail monitor, UI refresh loop (event scheduling)                                                                                |
| Data Granularity        | Per session (≥30s)          | Aggregated into day/week/month/year                                                                                                   |
| Recent Activities View  | Last 50                     | Editable table                                                                                                                        |
| Average Refresh Cadence | 2s                          | UI update loop                                                                                                                        |
| Idle Threshold          | 5 min                       | Session auto-suppression when idle                                                                                                    |

## 4. Architecture Overview

Layered modular design separating capture, classification, enforcement, session logic, persistence, and presentation.

1. Capture Layer: `activity_monitor.py`
   - Polls active window (Win32 APIs + psutil), segments usage into sessions, ignores idle intervals.
2. Classification Layer: `category_engine.py`
   - Keyword / process name heuristic mapping into one of four productivity categories; flags pseudo‑productive usage heuristics (e.g., entertainment patterns).
3. Focus Session Orchestration: `focus_manager.py`
   - Handles timing, pause/resume, completion detection, Deep Work vs Quick Focus durations, automatic jail activation for Deep Work, jail lifecycle safety on early termination.
4. Enforcement Layer: `productivity_enforcer.py`
   - Hosts file mutation (requires admin), process termination loop, limited YouTube content allow‑list, state persistence + monitoring loop.
5. Persistence Layer: `data_logger.py`
   - Per‑day JSON file, session append model, live daily summary accumulation (category totals, context switches, pseudo minutes), manual override save file.
6. Analytics Layer: `stats_calculator.py`, `trend_analyzer.py`
   - Aggregate daily records into weekly (per-day breakdown), monthly (category distribution), yearly (quarter summaries) views.
7. Presentation Layer: `dashboard.py`
   - ttk.Notebook UI: Focus timer + jail state; Activities editable tree; Statistics dynamic renderer with segment bars.

## 5. Data Model Highlights

Daily File Structure (sample keys):

```
{
  "date": "YYYY-MM-DD",
  "sessions": [ { start_time, end_time, application, window_title, category, duration_minutes, is_pseudo_productive } ... ],
  "daily_summary": {
    building, studying, applying, knowledge,
    pseudo_productive, context_switches, total_productive
  }
}
```

Supplements: `enforcement_state.json` (active jail end time), `activity_overrides.json` (manual log corrections), optional `hosts_backup.txt` (original hosts file snapshot).

## 6. Key Algorithms & Logic Decisions

- Session Segmentation: Starts new tracked session on process name change; discards micro-sessions < 30s (noise filtering).
- Idle Detection: Lightweight heuristic via `psutil.cpu_percent`; if below threshold and exceeds 5m window, suspends logging to avoid skew.
- Category Assignment: Rule-based heuristic (process + title tokens) for deterministic, explainable classification (transparent vs black-box ML at early stage).
- Productivity Jail Enforcement: Dual-phase—immediate hosts file rewrite + recurring 5s monitor loop (process kill + window title scan) with end-time-based auto-unblock.
- Deep Work Coupling: FocusManager automatically instantiates Enforcer; ensures teardown on session termination (even manual stop / completion boundary) to prevent orphaned blocking state.
- Race Condition Mitigation: Activities tab editing sets `_editing_activity` sentinel to skip refresh cycles preventing `TclError` from deleted row mid-edit.
- Incremental Statistics: Daily file holds cumulative counters → weekly/monthly aggregators avoid re-scanning raw event streams; O(n_days) not O(n_sessions) for higher-level summaries.

## 7. Notable Engineering Challenges & Resolutions

| Challenge                                             | Impact                                  | Resolution                                                                    |
| ----------------------------------------------------- | --------------------------------------- | ----------------------------------------------------------------------------- |
| Need to lock system during Deep Work automatically    | Risk of manual forgetfulness            | Auto-jail trigger in `start_focus_session` for 90m mode                       |
| Hosts file permission failures (non-admin run)        | Silent blocking failures                | Added explicit logging prompts to elevate when modification fails             |
| Activity editing conflicting with periodic refresh    | UI crashes (`TclError`) mid inline edit | Introduced `_editing_activity` guard + conditional refresh skip               |
| Prevent runaway pseudo micro-sessions                 | Data noise + inflated context switches  | Minimum 30s duration gating on session commit                                 |
| Avoid flicker & wasted compute in stats view          | Janky UX                                | Cached stats + rebuild only on range change (future optimization placeholder) |
| Need educational vs entertainment YouTube distinction | Over-blocking legitimate learning       | Allow‑list heuristic on channel/title substrings                              |
| Ensuring jail stops on early session termination      | Orphaned blocking state risk            | Centralized `_stop_jail_mode()` invocation inside end session logic           |

## 8. Security / Safety Considerations

- Writes to `C:\Windows\System32\drivers\etc\hosts` (admin rights required) – defensive backup + restore path.
- Process termination limited to curated blocklist; avoids terminating critical system processes.
- Local storage only; no external transmission of activity data.

## 9. Extensibility Roadmap (Future Upsell Talking Points)

- ML-based adaptive categorization (model fine-tunes heuristics per user behavior).
- Cross-device sync via encrypted lightweight backend (SQLite + sync API).
- Focus "streak" gamification and burnout detection (detect over-extension patterns).
- Export/Report generator (PDF weekly summary + heatmaps).
- Rule editor UI (user-managed allow/deny patterns + regex channels).
- Granular window-level timeline visualization.
- Smart break recommender using rolling cognitive load estimation.

## 10. Resume-Ready Achievement Bullets (Selectable)

- Built a local-first ADHD productivity platform that auto-classifies desktop activity into 4+ categories and distinguishes pseudo-productive time without manual input.
- Engineered an integrated distraction enforcement system (40+ domains, 25+ processes) with automatic activation during 90‑minute Deep Work sessions.
- Designed a modular architecture (capture → classify → enforce → persist → analyze → present) across ~1.3K lines of Python for maintainability and rapid iteration.
- Implemented race-condition-safe inline activity editing in a live-refreshing tkinter dashboard (refresh cycle every 2s) using an editing sentinel strategy.
- Developed multi-range analytics (day/week/month/year) with efficient aggregation avoiding reprocessing raw session streams.
- Added resilience features: idle suppression, minimum session duration filtering, safe teardown of blocking state, enforcement state persistence + recovery.

## 11. Talking Points (Interview / Demo)

1. Why rule-based first: Deterministic transparency builds trust; defers ML complexity until labeled dataset exists.
2. Enforcement coupling: Automatic Deep Work jail eliminates willpower reliance—systemic friction removal principle.
3. Data integrity: Minimum session length + idle filtering drastically reduce noise vs naive window pollers.
4. UI pragmatism: Three-tab split reduces cognitive load; inline edit improves correction speed vs modal forms.
5. Failure modes: Graceful degradation when not run as admin (tracking continues; enforcement warns instead of crashing).
6. Extensibility seams: Each layer swappable—e.g., classification engine can be replaced with ML classifier without touching UI or data model.
7. Ethical stance: Local-only storage ensures privacy; user retains control; no hidden telemetry.

## 12. Limitations / Honest Disclosures

- Enforcement strength limited when app not run elevated (web block bypassable).
- Classification heuristic can mislabel edge-case application titles (no NLP/ML yet).
- No real-time GPU/memory instrumentation or deep OS hooks (lightweight design choice).
- Manual override edits currently stored separately (not merged back into source sessions).

## 13. Tech Stack Summary

- Language: Python 3.x
- UI Framework: tkinter (ttk)
- System APIs: Win32 (window enumeration), hosts file modification
- Monitoring: psutil (process + CPU activity)
- Storage: JSON flat files (daily granularity + override / enforcement state files)
- Concurrency: Threading (enforcement monitoring) + Tk event loop scheduling

## 14. High-Level Flow (Deep Work Session)

1. User selects Deep Work (90m) → FocusManager initializes session
2. Jail auto-start: hosts file backup + block entries + process+window monitor thread
3. ActivityMonitor logs application shifts → DataLogger appends sessions
4. Dashboard refresh loop updates timer, jail status, activity label, stats
5. Session completes or user stops early → jail teardown → session metrics finalized
6. Aggregators consume daily file for statistical views

## 15. Potential Metrics to Track Next (For Iteration)

- Focus completion rate (%) over rolling 14 days
- Average uninterrupted deep focus block length
- Pseudo-productivity ratio = pseudo_minutes / (pseudo + productive)
- Category drift detection (variance week-over-week)
- Enforcement override attempts (if implementing bypass tracking)

## 16. Suggested Future Refactors

- Introduce service registry / dependency injection to simplify testing.
- Abstract file I/O behind repository interfaces for easier migration to SQLite.
- Implement event bus for decoupled UI updates instead of periodic polling.
- Add unit test harness (pytest) for category mapping and session edge cases.

## 17. Quick Copy Snippets (Concise Resume Lines)

> Built a modular ADHD productivity tracker (~1.3K LOC Python) that auto-classifies work vs pseudo-productive behavior and enforces distraction blocking during Deep Work.

> Implemented a hosts-file + process-kill enforcement layer with educational YouTube allow-list and automatic activation tied to 90-minute Deep Work sessions.

> Designed a race-condition-safe editable activity log and multi-range analytics (day/week/month/year) with lightweight JSON persistence.

## 18. Summary Sentence

A privacy-preserving, enforcement-integrated desktop productivity intelligence layer that transforms raw window activity into actionable, categorized deep work analytics while actively eliminating distractions.

---

Feel free to prompt a model with this file to generate tailored role-specific resume bullets, a portfolio case study, or a demo script.
