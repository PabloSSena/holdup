# 03: History page

**What to build:** The History page from the design (the "HISTORY" block): Last 7 days / Last 30 days segmented toggle; "Good Posture per day" bar chart painted with QPainter (empty days as a thin `ln` stub, % labels above bars in the 7-day view, day labels "Today" / weekday, or every 5th date in the 30-day view, tooltips); "Average N% across M days with Watched Time"; the Daily Stats table (Day: Today / Yesterday / "Wed 14 Oct"; Watched Time; Good Posture %, Forward Lean %, Side Lean %, Mirror; empty days read "No Watched Time"); Clear statistics with the in-window confirm dialog ("Delete all Daily Stats?" / "Your Baseline and settings are kept." / Cancel / Delete Daily Stats); and the empty state ("No Daily Stats yet"). Data from `monitor.daily_stats(first, last)`, re-read when the page is shown.

**Blocked by:** 01

**Status:** ready-for-agent

- [x] 7 and 30 day views show chart and table matching the design
- [x] Days without Watched Time are empty, never 0%
- [x] Clear statistics asks in-window, then empties Daily Stats and shows the empty state; Baseline and settings stay
- [x] Clear statistics is disabled when there are no Daily Stats
- [x] Tests: a pure function turning Daily Stats into table rows and chart points (labels, shares, average, empty days)

## Comments

**Done (worktree branch off build/posture-monitoring at a42c773).** `ui/history.py`: the pure `history(stats, today, days) -> History` (rows newest first with Today / Yesterday / "Wed 14 Oct", Watched Time as "4 h 36 min", shares and Mirror count; bars oldest first labelled Today / weekday, or every 5th date in the 30-day view; the average over days with Watched Time and their count; a day without Watched Time is an empty row and a `None` bar, never 0%), plus `HistoryPage`, the QPainter `_Chart` (tooltips "Good Posture 71%" / "No Watched Time") and `_Confirm`, the in-window confirm dialog (a scrim parented to the main window that follows its size; Escape cancels). `theme.py`: rules appended, scoped under `#history` and `#confirm` (plus a global `dialog-title` role) so they cannot clash with the other pages' rules. `windows.py`: `stats_cells()` and `STATS_COLUMNS` moved into `history.py`; `tests/test_stats_cells.py` folded into the new `tests/test_history.py` (6). Full suite: 95 pass.

- `refresh()` re-reads the last 7 or 30 days and rebuilds only when the resulting `History` differs from the one shown, so ticks with unchanged Daily Stats do nothing. "Today" is `date.today()` (the Posture Monitor's clock is not public; it is `datetime.now` in the app).
- The empty state and the disabled Clear statistics follow whether any Daily Stats exist at all (a second, whole-range read only when the shown range is empty). Daily Stats that exist only outside the range show the chart with stubs and "No Watched Time in these days", a case the design does not cover.
- Day and month names are fixed English tuples, not `strftime`, which follows the C locale.
- The average is the mean of the shown (rounded) daily shares, so it adds up with the bars; "1 day" is singular.
- Not in the design: the dialog narrows to the window width minus 48 px; the last 30-day label is kept inside the chart. Baseline and settings staying after Clear statistics is covered by the existing `tests/test_daily_stats.py`.

Checked: `grab()` screenshots with seeded in-memory Daily Stats (the design's 30-day data set): 7 and 30 days in light and dark, the confirm dialog in light and dark, Delete then the empty state (Daily Stats gone, Clear statistics disabled) in both themes, and 780 px wide; refreshing twice without a change keeps the same row widgets, and a change rebuilds them. Not checked by hand: hovering bars for the tooltips, clicking in the running app, a real Windows theme change. Near the 760 px minimum width the "Good Posture" column header touches its column's edge.
