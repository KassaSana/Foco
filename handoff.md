# Foco implementation handoff

## Resume here — user requested Terra Medium

The user is almost out of usage and explicitly wants to continue in a NEW session
using GPT-5.6 Terra with medium reasoning. Stop the current expensive-model run
after saving this handoff and committing the current recovery chunk. No tool is
available to create a conversation or switch the active model. The user must
select Terra / Medium and open a new session in this workspace. Do not spawn an
agent as a substitute for a new session.

Latest implemented chunk: `Restore focus timers after restart` (find hash with
git log). 68 tests passed, including eight new recovery tests. FocusManager now
writes focus_state.json in the logger's data directory at transitions, assigns
stable IDs/history dates, retries failed writes, replays pending completion
without duplicates, restores running/paused timers, and caps expired sessions
at their original deadline. Startup recovers blocking before the timer; Focus UI
restores buttons and displays persistence errors. Missing Deep Work blocking
recovers the timer paused. No real hosts file or user history used in tests.

NEXT: finish safe shutdown and recovery edge cases before classification. Closing
the window still exits the daemon blocker without cleanup. Add a clear close flow
that pauses/saves the timer and removes blocking, refusing silent success when
cleanup or persistence fails. Consider unsaved activity edits too. Verify with
mocked UI and temporary data. Also provide a recoverable UI action for corrupt
focus_state.json (currently preserved and prevents new sessions), validate saved
pause timestamps/elapsed relationships more fully, and check paused Deep Work
recovery if stale blocking remains. Desktop appearance has not been inspected.

Then continue ALL items in Remaining scope below. One coherent feature/fix per
commit, concise messages, existing Git identity, no attribution trailers.

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

Completion storage prerequisite now implemented: log_focus_session accepts an
optional stable id and history_date, deduplicates retries on that date, atomically
writes historical/current records, and rolls back in-memory changes on disk errors.
60 tests passed for that prerequisite. Commit: `Make focus history safe to retry`.
The session manager integration is now implemented as described in Resume here.

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
- Shared owner, explicit pause semantics, rule snapshots, and active timer recovery
  are implemented. Next finish safe close behavior and the recovery edges listed
  in Resume here.
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

## Latest continuation

Safe shutdown and recovery edge cases are now implemented. The window close flow
prompts through the existing activity editor for unsaved changes, checkpoints an
active focus timer as paused, removes remaining blocking, and keeps the window
open with an error if persistence or cleanup fails. Focus recovery rejects future
timestamps and inconsistent pause/completion values. The Focus tab offers a
confirmed, blocking-aware action to clear a corrupt saved checkpoint. Regression
coverage brings the full suite to 75 passing tests. Commit this chunk as one
feature before continuing with honest classification.

Honest classification is now implemented and verified in 79 tests. Unknown
windows are classified as Unclassified with a stored matching reason and are
excluded from productive summaries. Browser titles match readable site stems,
the current activity display shows the reason, and Settings includes a live
classification preview using the editable app/title rules. The next remaining
feature is session intention/outcome.
