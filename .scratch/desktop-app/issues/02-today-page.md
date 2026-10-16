# 02: Today page

**What to build:** The Today page from the design (the "TODAY" block): the status card (title, "since HH:MM", one-line explanation; "Paused until 14:30" or "Paused until resumed"), Pause for 30 minutes / Pause for 1 hour / Pause until resumed (the active one highlighted), Resume while paused, Recalibrate; the Watched Time card (total, stacked bar, Good Posture / Forward Lean / Side Lean as % and h/min); the Mirror card ("N times today"); the Camera Unavailable banner (Try again closes the camera so the next tick reopens it; "Choose another camera" goes to Settings) and the Stale Baseline banner (Recalibrate). Copy exactly as in the design. Refreshes on the tray tick while visible.

Needs from the monitor: `paused_until` (a datetime, or None for "until resumed"; add a read-only property). "since" is the time the displayed status label last changed; tracking it in the page is fine.

**Blocked by:** 01

**Status:** ready-for-agent

- [x] Every status from the design shows its title, since-time and explanation
- [ ] Pause buttons pause for the right duration and the chosen one is highlighted; Resume resumes; tray icon and menu stay in sync
- [x] Watched Time card shows today's numbers from `monitor.today_stats()`; zero Watched Time shows 0 min and an empty bar
- [x] Banners show only in Camera Unavailable / Stale Baseline, and their buttons work
- [x] Tests: `paused_until` through the Posture Monitor, and a pure formatter for "3 h 16 min" / "58 min"

## Comments

**Done (worktree branch off build/posture-monitoring at a42c773).** `ui/today.py` is the page: header with today's date, the Camera Unavailable and Stale Baseline banners, the status card (halo and dot in the status colour, title, "since HH:MM" for Watching / Absent / Camera Unavailable as in the design, explanation), Resume / the three Pause buttons / Recalibrate, the Watched Time card (total, painted stacked bar, three rows of % and duration) and the Mirror card. Pure helpers in the same module: `format_duration()` ("3 h 16 min", "58 min", whole minutes rounded down) and `headline()` (title and explanation, built on `theme.status()` so it always agrees with the pill and the tray icon). `PostureMonitor.paused_until` (None for a Pause until resumed, and when not paused). `Actions.retry_camera` (last field), wired to `camera.close` in `tray.py`; `CameraSource.close()` now also clears the 3 s reopen wait, otherwise Try again did nothing while the camera was already closed (a failed read still waits 3 s, as before). Tests: new `tests/test_today.py` (5). Full suite: 96 pass.

- Styles: the page sets its own small stylesheet from the theme tokens on top of the main window's (roles `status`, `small`, `heading`, `total`, `count`, `kind`, `share`, `rule`, `pause` / `pause-on`, `ghost`, `banner`); `theme.py` is unchanged.
- The page reads the theme the same way `MainWindow` does and re-applies its styles on the next `refresh()` after a theme change.
- Pause highlight: Pause until resumed is always highlighted while paused that way; a timed Pause is highlighted only when it was started from this page (the Posture Monitor knows the end time, not which button set it), so a 30-minute Pause from the tray menu shows no highlighted button.
- "since" is when the page first saw the current status label, so right after launch it reads the launch time.
- The button row wraps like the design: when Resume, the three Pause buttons and Recalibrate do not fit, Recalibrate moves to a second row (happens while paused at 960 px).
- Qt reads `#RRGGBBAA` as `#AARRGGBB`, so the halo uses `rgba(..., 46)` for the design's `color + '2E'`.

Checked: `QWidget.grab()` screenshots of the real `MainWindow` with an in-memory monitor in light and dark: Watching, Paused until 14:30 (30-minute button highlighted, Resume shown, Recalibrate wrapped), Paused until resumed with zero Watched Time (0 min, 0%, empty bar, 0 times today), Camera Unavailable banner, Stale Baseline banner, and 780 px wide with the icon sidebar. Clicking Try again called `retry_camera`; Choose another camera switched to Settings. `python -m holdup` ran 12 s with a scratch `LOCALAPPDATA` without Python errors (no camera here, so it stayed Camera Unavailable and retried every 3 s). Not checked by hand (so box 2 stays open): the tray icon and menu following a Pause / Resume from the page (it calls the same `pause` / `resume` as the menu, which call `show_state()`), Try again reopening a real camera, and the page refreshing live on the tick in the running app.
