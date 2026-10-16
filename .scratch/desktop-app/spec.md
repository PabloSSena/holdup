# Spec: Holdup desktop app (main window)

## Problem

Holdup lives only in the tray. Everything the User can do sits in a right-click menu, and the only statistics view is a bare table. The User wants a proper desktop window to see their posture statistics and do everything the tray menu does.

## Solution

One main window, rebuilt in PySide6 Qt Widgets from the Claude Design prototype in `design/Holdup.dc.html` (read it: it is the source of truth for layout, copy, colours and states; `design/support.js` is only the prototype's runtime, ignore it). No QtWebEngine and no new Python dependency (ADR 0002).

- **Shell:** custom-styled window (native Windows title bar is fine; the prototype's title bar is just a stand-in), a sidebar with Today / History / Settings and a live status pill at the bottom. Light and dark themes follow the Windows app theme. Default 960×640, minimum 760×520; below ~900 px wide the sidebar collapses to icons (60 px). Closing the window hides it to the tray; the app keeps running.
- **Today:** live status card, Pause / Resume / Recalibrate, today's Watched Time split, Mirror count, banners for Camera Unavailable and Stale Baseline.
- **History:** last 7 / 30 days toggle, Good Posture per day bar chart, Daily Stats table, Clear statistics with an in-window confirm dialog, empty state.
- **Settings:** Sensitivity, Camera, Baseline status + Recalibrate, Start with Windows, privacy note.
- **Calibration:** a full view over the window's content (Ready → countdown → hold → success / not in view / camera can't be read), replacing today's `CalibrationWindow`.
- **Mirror:** same window, plus a 3 px coloured inner edge and a label: amber "Forward Lean", periwinkle "Side Lean".
- **Icons:** tray icons with a glyph per state (so state reads without colour) and an app icon.

The tray stays: left-click opens the main window; the right-click menu keeps its current items, with "Stats" replaced by "Open Holdup".

## Design tokens (from the prototype)

| Token | Light | Dark | Use |
|---|---|---|---|
| bg | #F4F1EB | #161B19 | window background |
| sb | #ECE7DE | #1B211F | sidebar, segmented control track |
| cd | #FFFFFF | #222A27 | cards, selected nav / segment |
| ink | #1F2A26 | #E8EDEA | text |
| mu | #5E6A64 | #9BA6A1 | secondary text |
| ln | #E3DED4 | #313B37 | borders, dividers |
| sf | #F7F4EE | #1C2321 | input surfaces |
| ac / acs / aci | #2F7D62 / #E0EEE6 / #FFFFFF | #5DBB93 / #22382E / #0F1A15 | accent = Good Posture, its soft fill, text on accent |
| fw | #C27A26 | #E2A45C | Forward Lean |
| sd | #6870B5 | #A0A7E6 | Side Lean |
| wn / wni | #FBF0E1 / #7A4A12 | #33291C / #F1C58F | warning banner fill / ink |
| scrim | rgba(20,24,22,.38) | rgba(0,0,0,.55) | dialog backdrop |

Status colours: Watching #3FA36B, Absent #8C948F, Camera Unavailable #E07A2E, Stale Baseline #D9534F, Paused #E3B53B, Calibrating #4C8BD6. Font: Figtree 400/500/600/700 (falls back to Segoe UI). Cards: 16 px radius, 1 px `ln` border, 20×22 padding. Buttons: 10 px radius, 36 px high.

"Watching" in the UI covers the monitor states Good Posture, Forward Lean and Side Lean.

## Out of scope

- Live camera preview anywhere other than Calibration and the Mirror.
- A custom (frameless) title bar.
- Week/month aggregates beyond the 30-day view; exporting stats.
- macOS/Linux.

## Module layout

`src/holdup/ui/` holds the new window: `theme.py` (tokens + stylesheet), `main_window.py` (shell), one module per page (`today.py`, `history.py`, `settings.py`, `calibration.py`). Pages get the `PostureMonitor` and a small set of callbacks from `tray.py`, so each page can be built in its own branch without touching the others.
