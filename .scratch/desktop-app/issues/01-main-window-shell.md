# 01: Main window shell

**What to build:** The main window from the design (`../design/Holdup.dc.html`, the "WINDOW" block and the sidebar): theme tokens and a Qt stylesheet for light and dark (following the Windows app theme via `QGuiApplication.styleHints().colorScheme()`), Figtree bundled and loaded (OFL font files in `src/holdup/fonts/`, added to package-data and `Holdup.spec`; fall back to Segoe UI), a sidebar with Today / History / Settings and the live status pill, and three page slots. Closing the window hides it to the tray. Tray left-click and a new "Open Holdup" menu item (replacing "Stats") show and raise it. Below ~900 px wide the sidebar collapses to icons only.

Lay it out so the pages can be built in parallel later: `src/holdup/ui/theme.py`, `src/holdup/ui/main_window.py`, and placeholder pages `today.py`, `history.py`, `settings.py`, each a `QWidget` subclass taking the `PostureMonitor` (and later callbacks) with a `refresh()` method the tray tick calls while the window is visible. Also add `MainWindow.show_calibration()` as the slot issue 05 fills (until then it can open the existing `CalibrationWindow`).

**Blocked by:** none

**Status:** ready-for-agent

- [ ] Tray left-click and "Open Holdup" open the main window; closing it hides it and the app keeps running
- [ ] Sidebar switches between the three pages; the selected item uses the `cd` background
- [ ] Status pill shows the live state label and colour (Watching / Absent / Camera Unavailable / Stale Baseline / Paused / Calibrating), updated on the tray tick
- [ ] Light and dark themes match the spec's tokens and follow Windows
- [ ] Sidebar collapses to 60 px icons below ~900 px; minimum size 760×520
- [ ] The old Stats window and its tray item are gone (`stats_cells` may move or go; keep its tests passing or replace them)
- [ ] A pure helper mapping (MonitorState, paused) to status label and colour has a test
