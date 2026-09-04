# Foco repository guide

## Run and verify

- Install dependencies: `python -m pip install -r requirements.txt`
- Run with Windows elevation: `python app_launcher.py`
- Run without elevation: `python -m foco`
- Run tests: `python -m unittest discover -s tests -v`
- Build the executable: `python -m scripts.build_executable`

## Where code lives

- `foco/app.py` is the desktop composition root.
- `foco/activity_tracking/` owns foreground tracking and classification.
- `foco/focus/` owns focus sessions, jail blocking, and the Focus tab.
- `foco/activities/`, `foco/statistics/`, and `foco/settings/` own their tabs.
- `foco/config.py` and `foco/storage.py` are genuinely shared modules.
- Tests mirror the feature folders under `tests/`.
- Keep `config.json` and ignored `productivity_data/` at the repository root.

## Conventions

- Organize new code by feature or user flow, with boring searchable names.
- Feature-specific code stays with its feature; do not create generic `utils`,
  `services`, `helpers`, or `common` folders.
- Feature UI modules must not import other feature UI modules. Assemble features
  only in `foco/app.py`.
- Preserve local-data and hosts-file safety behavior.
- Avoid drive-by refactors, new abstractions, dependency upgrades, and unrelated
  rewrites.
