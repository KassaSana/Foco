# Foco implementation handoff

## Working agreement

Continue all improvements agreed in this conversation. Implement and verify one
feature or coherent fix per commit. Use the existing Git author/committer; never
add AI attribution or co-author/contributor trailers. Read AGENTS.md. Explain the
architecture before edits and report tests afterward. Do not touch real hosts
entries or user activity data during tests.

The user requested a new session at each feature boundary or 30% remaining
context. No callable new-conversation/session tool is available. Maintain this
file at boundaries and continue through the active goal; do not claim a new
session was opened. No subagents are authorized or needed.

## Completed

- `1328945` — Fix activity editing to preserve history. Full-day editor, retained
  metadata, Save/Cancel, dirty-state refresh protection, concurrent tracker append
  preservation, conflict/day checks, and disk-failure rollback. 40 tests passed.
- Timer stability chunk: preserve a focus session's captured duration across Settings
  changes; expose seconds directly to the timer; do not count an early stop as
  100% completion through rounding. All 43 tests passed. Commit message:
  `Keep focus timers stable when settings change`. Next: lifecycle item 1 below.
- Blocking ownership/error chunk: shared lazy enforcer owned by FocusManager;
  manual blocks cannot overlap focus sessions; pause releases Deep Work blocking,
  resume reapplies it for remaining time. Start/pause/resume failures preserve
  timer state; failed cleanup remains visible with Disable retry. Block state
  save failure rolls back hosts changes. Expired monitors retry cleanup without
  terminating applications. 52 tests passed before final diff review. Commit:
  `Unify focus blocking and report failures`. Lifecycle item 1 is still incomplete.

## Remaining scope (do not mark goal complete until verified)

Latest recovery chunk: enforcement_state.json now includes the original blocked
apps/sites. Live recovery validates and restores them instead of adopting changed
Settings. Legacy files use configured rules; expired cleanup ignores invalid rule
snapshots. Tests cover these paths using temporary hosts files. Next remains
active timer persistence/recovery and safe close behavior.

1. Reliable focus/blocking lifecycle: one enforcement owner shared by manual and
   Deep Work; explicit pause behavior; truthful start/stop errors; persisted active
   timer and restart recovery; clear safe close behavior. Preserve unrelated hosts
   entries and local data. Use temporary hosts files and injected/mocked enforcers.
2. Honest classification: Unclassified excluded from productive totals; matching
   reason visible; easy correction and persistent app/title rules; rule preview in
   Settings. Account for window titles not being URLs. Preserve old history.
3. Session intention/outcome: lightweight intention at start; Done/Progress/Blocked
   and optional note afterward; session history. Keep timer completion separate
   from reported outcome. Persist locally.
4. Completion notification with clear break / another-session / finish actions.
5. Improved measurement: retain short activity segments, separate app/title changes
   from meaningful context switches, group related productive segments into work
   blocks bounded by distraction or idle time.
6. Blocking preview before Deep Work/manual blocks (defaults include apps/sites
   needed for work), historical day navigation/correction, and compact daily review
   with outcomes, main distractions, and one evidence-grounded suggestion.

Items 5–6 were second-priority recommendations, not removed from the user's
request to finish all features. Avoid unrelated architecture rewrites, cloud
services, dependency upgrades, elaborate analytics, or AI advice.

## Next implementation notes

- Composition root: foco/app.py. UI features are mixins assembled there; feature
  UI modules must not import other feature UI modules.
- Shared owner and explicit pause semantics are now implemented. Next add active
  timer persistence/recovery and safe close behavior, with tests for running,
  paused, expired, interrupted, and failed-cleanup states. Persist the block list
  snapshot too so recovery doesn't silently adopt changed Settings.
- FocoApp.run finally only flushes activity; active focus sessions are not saved.
  Enforcement is a daemon thread and cannot clean hosts after process exit.
- Tests mirror features. Full check: python -m unittest discover -s tests -v.
  Inspect git diff and git diff --check, stage exact files, commit, inspect commit
  message/identity and clean status. Update this handoff in each relevant commit.

## Review findings still relevant

- Classifier defaults unknown games/titles to Knowledge; browser titles do not
  reliably contain configured domain strings. Pseudo flags are independent.
- Statistics defines work blocks as individual activity segments; monitor drops
  segments <=30 seconds. Existing tests encode that behavior and need updating.
- Statistics UI rebuilds even when hidden every two seconds; consider narrowly
  improving refresh behavior while implementing daily review, not a standalone
  broad refactor.
- Existing tests are headless. Desktop UI appearance has not been visually tested.
