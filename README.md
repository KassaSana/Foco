# Foco

Foco is a private, Windows-first desktop application for measuring meaningful work and creating friction against distractions. It tracks foreground activity, distinguishes productive work from pseudo-productivity, runs configurable focus sessions, and can block distracting domains and applications during committed work periods.

All activity history stays on the local machine as JSON. Foco has no account, cloud service, or telemetry.

## What Foco does

- Tracks foreground processes and window titles using Windows APIs.
- Splits browser tabs and document-title changes into separate activity segments.
- Uses configurable rules to classify time as Building, Studying, Applying, or Knowledge.
- Flags pseudo-productive activity separately from meaningful work.
- Tracks a configurable daily distraction budget and suggests Quick Focus when it is reached.
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

`app_launcher.py` requests elevation automatically. Foco can also be started without elevation using `python -m foco`.

## Project layout

```text
foco/                     Application package
  app.py                  Desktop composition root
  config.py               Shared configuration loading and validation
  storage.py              Shared local JSON persistence
  activity_tracking/      Foreground tracking and classification
  focus/                  Focus sessions, blocking, and Focus tab
  activities/             Editable activity timeline tab
  statistics/             Historical metrics and Statistics tab
  settings/               Settings tab
scripts/                  Executable packaging utility
tests/                    Tests mirroring the feature folders
app_launcher.py           Elevated Windows entry point
config.json               User-editable defaults
```

## Using the application

The Focus tab starts timed sessions, shows today's distraction-budget usage, and controls Focus Jail. Deep Work starts jail automatically; the shorter Quick Focus mode does not. Reaching the distraction budget offers Quick Focus but never starts blocking automatically.

The Activities tab shows the canonical timeline for the current day. Add, edit, or delete rows and select Save to recalculate the day's statistics from those changes.

The Statistics tab shows category totals and focus-quality metrics across four time ranges.

The Settings tab controls session durations, idle timeout, the daily distraction budget, category patterns, pseudo-productivity rules, blocked domains, and blocked executable names. Set the distraction budget to `0` to disable its alert. Enter one rule per line. Blocking changes take effect when the next jail starts.

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

Run `python -m scripts.build_executable` to build `dist/Foco.exe` with PyInstaller.
