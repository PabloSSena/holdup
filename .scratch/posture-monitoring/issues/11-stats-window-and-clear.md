# 11: Stats window and Clear statistics

**What to build:** A Stats item in the tray menu opens a small window showing today and the last 7 days: the share of Watched Time in Good Posture, Forward Lean and Side Lean, and the Mirror count. A Clear statistics button, with confirmation, deletes all Daily Stats while keeping the Baseline and settings.

**Blocked by:** 10

**Status:** ready-for-agent

- [x] The Stats window shows today and each of the last 7 days as percentages of Watched Time, plus the Mirror count
- [x] Days with no Watched Time are shown as empty rather than 0% Good Posture
- [x] Clear statistics asks for confirmation, then removes all Daily Stats
- [x] Clearing keeps the Baseline and settings intact
- [x] Tests through the Posture Monitor cover Clear Stats emptying Daily Stats while the Baseline survives

## Comments

**Done (worktree branch off build/posture-monitoring).** Changed: `store.py` (`clear_daily_stats()`: `DELETE FROM daily_stats`; the `setting` table is untouched), `posture_monitor.py` (`clear_stats()`), `windows.py` (`stats_cells()`, a pure row formatter, and `StatsWindow`), `tray.py` (a "Stats" item at the top of the menu, plus creating the window). Tests: one in `tests/test_daily_stats.py` (Clear Stats through the Posture Monitor on a real SQLite file: Daily Stats are empty, and after a restart the Baseline still judges and the Sensitivity is kept), and a new `tests/test_stats_cells.py` (shares and Mirror count; a missing day or one with no Watched Time is blank). Full suite: 79 pass.

- The window is a fixed-size table: the rows are "Today" and then the 7 previous days ("Wed 14 Oct"). The columns are Good Posture, Forward Lean and Side Lean (whole-number percentages of Watched Time, so they may not add up to exactly 100), and Mirror (a count). It re-reads the Store each time it is shown, and does not update while it stays open.
- An empty day is blank in every column, including Mirror.
- Clear statistics asks with a Yes/No `QMessageBox` (default No), then clears and refreshes.
- The window takes today's date from `date.today()`. The tray's monitor clock is `datetime.now`, so the two agree.

Checked: rendered with seeded data in a scratch `LOCALAPPDATA` (the screenshot looked right); Clear run with the dialog stubbed to Yes (rows blank, setting kept); `python -m holdup` ran for 10 s without errors. Not checked by hand: clicking the tray item, and the real confirmation dialog.
