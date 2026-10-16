# 01: Main window shell

**What to build:** The main window from the design (`../design/Holdup.dc.html`, the "WINDOW" block and the sidebar): theme tokens and a Qt stylesheet for light and dark (following the Windows app theme via `QGuiApplication.styleHints().colorScheme()`), Figtree bundled and loaded (OFL font files in `src/holdup/fonts/`, added to package-data and `Holdup.spec`; fall back to Segoe UI), a sidebar with Today / History / Settings and the live status pill, and three page slots. Closing the window hides it to the tray. Tray left-click and a new "Open Holdup" menu item (replacing "Stats") show and raise it. Below ~900 px wide the sidebar collapses to icons only.

Lay it out so the pages can be built in parallel later: `src/holdup/ui/theme.py`, `src/holdup/ui/main_window.py`, and placeholder pages `today.py`, `history.py`, `settings.py`, each a `QWidget` subclass taking the `PostureMonitor` (and later callbacks) with a `refresh()` method the tray tick calls while the window is visible. Also add `MainWindow.show_calibration()` as the slot issue 05 fills (until then it can open the existing `CalibrationWindow`).

**Blocked by:** none

**Status:** ready-for-agent

- [ ] Tray left-click and "Open Holdup" open the main window; closing it hides it and the app keeps running
- [x] Sidebar switches between the three pages; the selected item uses the `cd` background
- [x] Status pill shows the live state label and colour (Watching / Absent / Camera Unavailable / Stale Baseline / Paused / Calibrating), updated on the tray tick
- [x] Light and dark themes match the spec's tokens and follow Windows
- [x] Sidebar collapses to 60 px icons below ~900 px; minimum size 760×520
- [x] The old Stats window and its tray item are gone (`stats_cells` may move or go; keep its tests passing or replace them)
- [x] A pure helper mapping (MonitorState, paused) to status label and colour has a test

## Comments

**Done (worktree branch, fast-forwarded onto build/posture-monitoring after issues 06 and 07).** New `src/holdup/ui/`: `theme.py` (light/dark tokens, the stylesheet, `load_fonts()`, and `status()`, the pure (MonitorState, paused) to label and colour helper, built on `icons.tray_glyph`/`TRAY_COLORS` so the pill always matches the tray icon), `actions.py` (`Actions`, the callbacks the pages get), `main_window.py` (the shell), and placeholder `today.py`, `history.py`, `settings.py`. Figtree 400/500/600/700 static TTFs plus `OFL.txt` in `src/holdup/fonts/`, added to package-data and to `build.ps1` (`--add-data`; there is no checked-in `Holdup.spec`). `tray.py`: "Open Holdup" replaces "Stats", tray left-click opens the window, the window is refreshed from `show_state()` (each analysed frame, pause, resume, camera change) while visible, and a `set_sensitivity` callback keeps the tray menu's mark in step. `windows.py`: `StatsWindow` is gone; `stats_cells()` stays for the History page. Tests: new `tests/test_status.py` (4). Full suite: 91 pass.

- Page interface: `Page(monitor: PostureMonitor, actions: Actions)`, a `QWidget` with `refresh()`. The shell wraps each page in a scroll area; pages set `theme.PAGE_MARGINS` on their own layout and style widgets with `setProperty("role", ...)`: `title`, `muted`, `card` (`theme.CARD_MARGINS`), `primary` button.
- Navigation from a page: `self.window().show_page("Settings")`.
- `MainWindow.show_calibration()` still shows the old `CalibrationWindow` (now owned by the main window as `main_window.calibration`, which the tick feeds). The caller begins Calibration first.
- Uncalibrated (no Baseline, first Calibration failed) shows as Calibrating, like the tray icon; the design has no state for it.
- The stylesheet is set on the main window only, so the tray menu, Mirror and Calibration window keep their look.
- Closing with the title-bar button hides the window (spontaneous close events only), so Quit still exits.
- Figtree comes from the upstream repo (erikdkennedy/figtree) because google/fonts only ships the variable font; the OFL is from google/fonts.

Checked: screenshots via `QWidget.grab()` in light, dark (switched with `styleHints().setColorScheme`, which also checked the live theme switch) and 780 px wide (60 px icon sidebar, Paused pill); Qt lists all four Figtree weights and the labels render in Figtree; `python -m holdup` ran 12 s with a scratch `LOCALAPPDATA` without Python errors. Not checked by hand: clicking the tray icon and "Open Holdup", the title-bar close button hiding the window, and a real Windows theme change while running.
