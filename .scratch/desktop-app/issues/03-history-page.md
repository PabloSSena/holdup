# 03: History page

**What to build:** The History page from the design (the "HISTORY" block): Last 7 days / Last 30 days segmented toggle; "Good Posture per day" bar chart painted with QPainter (empty days as a thin `ln` stub, % labels above bars in the 7-day view, day labels "Today" / weekday, or every 5th date in the 30-day view, tooltips); "Average N% across M days with Watched Time"; the Daily Stats table (Day: Today / Yesterday / "Wed 14 Oct"; Watched Time; Good Posture %, Forward Lean %, Side Lean %, Mirror; empty days read "No Watched Time"); Clear statistics with the in-window confirm dialog ("Delete all Daily Stats?" / "Your Baseline and settings are kept." / Cancel / Delete Daily Stats); and the empty state ("No Daily Stats yet"). Data from `monitor.daily_stats(first, last)`, re-read when the page is shown.

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] 7 and 30 day views show chart and table matching the design
- [ ] Days without Watched Time are empty, never 0%
- [ ] Clear statistics asks in-window, then empties Daily Stats and shows the empty state; Baseline and settings stay
- [ ] Clear statistics is disabled when there are no Daily Stats
- [ ] Tests: a pure function turning Daily Stats into table rows and chart points (labels, shares, average, empty days)
