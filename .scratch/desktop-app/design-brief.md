# Design brief: Holdup desktop app

Paste everything below the line into Claude Design.

---

Design a desktop app window for **Holdup**, a Windows 10/11 app that watches the user's sitting posture through their own webcam and warns them when it degrades. Camera frames never leave the machine and are never stored; only numbers are kept. Today it lives only in the system tray; this window becomes its main home. The tray icon stays, and closing the window hides it back to the tray.

Tone: calm, friendly, health-app, not clinical and not gamified. Light and dark themes. Window around 960×640, resizable down to about 760×520. It will be rebuilt in Qt (PySide6), so prefer flat surfaces, rounded cards, simple charts; avoid blur/glass effects and web-only tricks.

Use these exact words in the UI: Baseline, Calibration / Recalibrate, Sensitivity (Low / Medium / High), Good Posture, Forward Lean, Side Lean, Mirror, Pause / Resume, Watched Time, Daily Stats.

## Screens

1. **Today (home)**
   - Live status, one of: Watching, Absent (nobody in front of the camera), Camera Unavailable (unplugged, covered or used by another app), Stale Baseline (camera view changed, needs Recalibrate before watching resumes), Paused (with "until 14:30" or "until resumed"), Calibrating.
   - Today's Watched Time split into Good Posture / Forward Lean / Side Lean (as % and hours/minutes), and how many times the Mirror appeared.
   - Quick actions: Pause for 30 minutes, Pause for 1 hour, Pause until resumed, Resume (only while paused), Recalibrate.
   - Stale Baseline and Camera Unavailable need a clear, non-alarming banner with the fix.

2. **History**
   - Daily Stats per day: Good Posture %, Forward Lean %, Side Lean %, Mirror count. Show the last 7 days and the last 30 days (toggle). A day with no Watched Time shows as empty, not 0%.
   - A trend chart of Good Posture % per day.
   - "Clear statistics" button with a confirm dialog: "Delete all Daily Stats? Your Baseline and settings are kept."

3. **Settings**
   - Sensitivity: Low / Medium / High, with a one-line explanation (how far from your Baseline you may sit before it counts as Bad Posture).
   - Camera: a dropdown of connected cameras, or "No camera found". Note that switching camera makes the Baseline Stale.
   - Start with Windows: toggle.
   - Privacy note: frames never leave this computer and are never saved.

4. **Calibration** (modal or full view; shown on first launch and on Recalibrate)
   - Large live camera preview (4:3), instruction "Sit up straight, the way you want to sit, facing your screen."
   - States: countdown "Capturing in 3…", "Hold still…", success "Your Baseline is captured. Holdup is now watching your posture.", failure "Make sure you are in view and hold still" with Retry, and failure "The camera can't be read" with Retry.

5. **Mirror** (separate tiny window, keep it minimal)
   - 320×240 frameless, always-on-top, bottom-left of the screen, showing only the live camera feed when Bad Posture has lasted too long. Optionally a thin colored edge or small label "Forward Lean" / "Side Lean". Nothing clickable.

## Also design

- Tray icon colors per state (currently: green Watching, grey Absent, orange Camera Unavailable, red Stale Baseline, yellow Paused) and the app icon.
- Empty state for History when there are no Daily Stats yet.
