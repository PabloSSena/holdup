# 02: Today page

**What to build:** The Today page from the design (the "TODAY" block): the status card (title, "since HH:MM", one-line explanation; "Paused until 14:30" or "Paused until resumed"), Pause for 30 minutes / Pause for 1 hour / Pause until resumed (the active one highlighted), Resume while paused, Recalibrate; the Watched Time card (total, stacked bar, Good Posture / Forward Lean / Side Lean as % and h/min); the Mirror card ("N times today"); the Camera Unavailable banner (Try again closes the camera so the next tick reopens it; "Choose another camera" goes to Settings) and the Stale Baseline banner (Recalibrate). Copy exactly as in the design. Refreshes on the tray tick while visible.

Needs from the monitor: `paused_until` (a datetime, or None for "until resumed"; add a read-only property). "since" is the time the displayed status label last changed; tracking it in the page is fine.

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] Every status from the design shows its title, since-time and explanation
- [ ] Pause buttons pause for the right duration and the chosen one is highlighted; Resume resumes; tray icon and menu stay in sync
- [ ] Watched Time card shows today's numbers from `monitor.today_stats()`; zero Watched Time shows 0 min and an empty bar
- [ ] Banners show only in Camera Unavailable / Stale Baseline, and their buttons work
- [ ] Tests: `paused_until` through the Posture Monitor, and a pure formatter for "3 h 16 min" / "58 min"
