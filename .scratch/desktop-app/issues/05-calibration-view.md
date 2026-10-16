# 05: Calibration view in the main window

**What to build:** The Calibration view from the design (the "CALIBRATION" block) as a full overlay on the main window's content, replacing `CalibrationWindow`: 4:3 live preview (480 px wide, 352 at minimum window size) with the head/shoulder guide outline and the "Live preview" tag; states Ready (Start) → "Capturing in 3…" (big number over the feed) → "Hold still…" (progress bar) → success (Done) / "Make sure you are in view and hold still" (Retry) / "The camera can't be read" (No picture, Retry). Cancel shows in every state except success. First launch and every Recalibrate (tray menu, Today, Settings, Stale banner) open this view and show the main window.

Needs from the monitor: `cancel_calibration()`, which ends a calibration in progress without changing the Baseline and returns to normal judging (Stale stays Stale); and capture progress (0..1) for the hold bar, derived from the existing countdown and capture timing.

**Blocked by:** 01

**Status:** ready-for-agent

- [x] Every state from the design is reachable with the real monitor and shows the design's copy
- [x] Start begins the countdown; Retry restarts; Done closes the view; Cancel leaves the old Baseline untouched
- [x] The feed only runs while the view is visible, and frames are still never kept
- [x] The old `CalibrationWindow` is removed
- [x] Tests: `cancel_calibration()` and capture progress through the Posture Monitor

## Comments

**Done (worktree branch off build/posture-monitoring at a42c773).** New `src/holdup/ui/calibration.py`: `CalibrationView` (the main window's `calibration`, still fed by the tray tick through `isVisible()/refresh()/show_frame()`) and `_Preview`, which paints the 4:3 preview: the feed scaled to fill (cropped, mirrored), the head-and-shoulders outline (dashed white, solid green on hold/success, dashed amber on "not in view"), the "Live preview" tag, the big countdown number, the hold bar, the success check, and "No picture" when the camera can't be read. The view's state comes from the Posture Monitor once Start or Retry has been pressed: Calibrating with countdown left is the countdown, then the hold; after it, success or a failure (Camera Unavailable picks the camera copy). `main_window.py`: the central widget is now a stack (shell, Calibration), so the view covers the sidebar too, below the native title bar; `show_calibration()` resets the view to Ready and presents the window; Done goes to Today, Cancel back to the page the User was on; `_set_compact` switches the preview to 352 px. `posture_monitor.py`: `cancel_calibration()` and `calibration_progress()` (0..1 of the 2 s capture), next to `begin_calibration()`; `_end_calibration` untouched. `tray.py`: first launch and `recalibrate()` only show the view; Calibration begins on Start. `windows.py`: `CalibrationWindow` is gone; `_pixmap` takes an aspect mode. Tests: new `tests/test_calibration.py` (3). Full suite: 94 pass.

- Ready precedes the countdown as in the design, so `begin_calibration()` now runs on Start/Retry, not on Recalibrate. Until Start the monitor keeps judging as before (Uncalibrated on first launch, Stale stays Stale).
- Opening the view again (any Recalibrate entry point) while a Calibration is running cancels it and shows Ready.
- After `cancel_calibration()` the monitor state stays Calibrating until the next analysed frame (at most about a second).
- The view keeps only the last frame's pixmap for painting, like the Mirror, and drops it when hidden or reopened. Frames are never written anywhere.
- Kicker colour reads the theme tokens on each refresh, so a theme switch shows up on the next tick; sizes live in the view's own colourless stylesheet, colours come from the main window's.
- CSS line-heights (1.25/1.5) are not reproduced; Qt's default line spacing is a little tighter.

Checked: `grab()` screenshots of all six states driven through the real Posture Monitor with a fake clock and a fake frame, in light, dark and at 760x520 (352 px preview), compared with the design; Done and Cancel close the view. Ran the real app 14 s with a scratch `LOCALAPPDATA` (first launch, Uncalibrated): the window opened on Ready with the live mirrored feed, Start began the countdown and, with nobody sitting in front of the camera, ended on "Make sure you are in view and hold still". Not checked by hand: a successful real Calibration, the Retry after "The camera can't be read" on a real unplugged camera, Recalibrate from the tray menu and from Today/Settings/Stale banner (those pages are being built in parallel), and a live Windows theme change while the view is open.
