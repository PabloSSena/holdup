# 10: Record Daily Stats

**What to build:** While posture is being judged, Holdup records Daily Stats: seconds of Watched Time in Good Posture, Forward Lean and Side Lean, plus how many times the Mirror appeared. Days split at local midnight and data is kept indefinitely. Only judged time accumulates, so Paused, Absent, Stale Baseline and Camera Unavailable time never count.

**Blocked by:** 03, 04

**Status:** ready-for-agent

- [x] Daily Stats rows are stored in the Store keyed by local date, holding Good Posture, Forward Lean and Side Lean seconds and the Mirror count; Watched Time is their sum
- [x] The Mirror count increases by one each time the Mirror goes from hidden to visible
- [x] Time in any non-judging state (Absent, Paused, Stale Baseline, Camera Unavailable, Uncalibrated, Calibrating) adds nothing
- [x] Time crossing local midnight is split between the two days
- [x] Stats survive restarts and are never deleted automatically
- [x] The Posture Monitor exposes Daily Stats queries for today and a range of days
- [x] Tests through the Posture Monitor with a real temporary SQLite database cover time attribution per kind, the Mirror count, exclusion of Absent time, and the midnight split

## Comments

**Done (worktree branch off build/posture-monitoring).** Changed: `store.py` (a `daily_stats` table created in `Store.__init__`, plus `add_daily_stats()` and `daily_stats()` beside `get`/`set`), `posture_monitor.py` (`DailyStats`, `daily_stats()`, `today_stats()`, accounting in `observe()`), new `tests/test_daily_stats.py` (10 tests on a real SQLite file in `tmp_path`). No tray change: the tray already gives the monitor the on-disk Store. Full suite: 55 pass. Not checked in the real app. Stale Baseline exclusion is untested because issue 08 is being built in parallel (see the last bullet).

**Time attribution rule:** each `observe()` gives the interval since the previous observation to the previous observation's kind, if that observation was judged. An observation is judged when `state` is Good Posture, Forward Lean or Side Lean and the monitor is not Paused (one line: `None if self.paused else _STATS_COLUMN.get(self.state)`). Any other `MonitorState` (Absent, Camera Unavailable, Uncalibrated, Calibrating, and a future Stale state) adds nothing. An interval longer than `STATS_MAX_GAP` (5 s), or a negative one (clock set back), adds nothing at all, so sleep or hibernate never counts. An interval crossing local midnight is split at midnight, using the local time from the injected clock. Consequences: the last interval before a change (up to 0.4 s, or 1 s when idle) goes to the old kind, and the time after the latest frame is only counted at the next frame.

**Mirror count:** +1 on the local date of the frame where `mirror_visible` goes False → True.

Decisions issue 11 should know:
- **Queries**: `monitor.today_stats() -> DailyStats` (all zeros when nothing was recorded today) and `monitor.daily_stats(first: date, last: date) -> dict[date, DailyStats]`, both ends included, holding **only days that have a row**. Show a missing day, or one with `watched_time == 0`, as empty.
- `DailyStats` fields: `good_posture`, `forward_lean`, `side_lean` (seconds, float), `mirror_count` (int), and the property `watched_time` (their sum). Percentages: field / `watched_time`.
- Clear statistics: add a `Store` method doing `DELETE FROM daily_stats`. The Baseline and settings live in the `setting` table, so they survive.
- Writes are one SQLite commit per judged frame (~2.5/s), marked `shortcut:` in `_add_watched_time`.
- Issue 08: if Stale is its own `MonitorState`, nothing to do. If it is a flag on top of `state` (like Pause), add it to the `_judged_as` line at the end of `observe()`.
