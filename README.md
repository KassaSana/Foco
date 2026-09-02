# Foco

Foco is a private, Windows-first desktop application for measuring meaningful work and creating friction against distractions. It tracks foreground activity, distinguishes productive work from pseudo-productivity, runs configurable focus sessions, and can block distracting domains and applications during committed work periods.

All activity history stays on the local machine as JSON. Foco has no account, cloud service, or telemetry.

## What Foco does

- Tracks foreground processes and window titles using Windows APIs.
- Splits browser tabs and document-title changes into separate activity segments.
- Uses configurable rules to classify time as Building, Studying, Applying, or Knowledge.
- Flags pseudo-productive activity separately from meaningful work.
- Provides Quick Focus and Deep Work timers with pause, resume, and automatic completion.
- Automatically enables Focus Jail for Deep Work sessions.
- Blocks configured domains through the Windows hosts file and closes configured applications.
- Recovers active blocking after a restart and removes expired or stale rules safely.
- Stores editable daily activity and focus history locally.
- Reports daily, weekly, monthly, and yearly totals, focus completion, work-block length, and pseudo-productivity ratio.

## Requirements

- Windows 10 or newer
- Python 3.7 or newer
- Administrator privileges for Focus Jail

Foreground tracking can run without elevation. Domain blocking requires administrator access because it modifies the Windows hosts file.

## Run from source

```powershell
git clone https://github.com/KassaSana/Foco.git
cd Foco
python -m pip install -r requirements.txt
python app_launcher.py
```

Use `run_as_admin.bat` for a launcher that requests elevation. Run `python install.py` for the guided first-time setup.

## Using the application

The Focus tab starts timed sessions and controls Focus Jail. Deep Work starts jail automatically; the shorter Quick Focus mode does not.

The Activities tab shows the canonical timeline for the current day. Add, edit, or delete rows and select Save to recalculate the day's statistics from those changes.

The Statistics tab shows category totals and focus-quality metrics across four time ranges.

The Settings tab controls session durations, idle timeout, category patterns, pseudo-productivity rules, blocked domains, and blocked executable names. Enter one rule per line. Blocking changes take effect when the next jail starts.

## Local data

Foco writes one file per day under `productivity_data/`:

```text
productivity_data/
  2026-09-02.json
  enforcement_state.json
  hosts_backup.txt
```

Daily files contain activity sessions, focus sessions, and cumulative summaries. Enforcement state allows a live jail to resume after the interface restarts. Foco removes only the hosts-file section it owns and preserves unrelated entries.

## Tests

```powershell
python -m unittest discover -s tests -v
```

The tests use temporary hosts and data files; they do not modify the system hosts file or terminate applications.

## Packaging

Run `python setup_app.py` and choose the executable option to build `dist/Foco.exe` with PyInstaller.
