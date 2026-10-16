# 05: Calibration view in the main window

**What to build:** The Calibration view from the design (the "CALIBRATION" block) as a full overlay on the main window's content, replacing `CalibrationWindow`: 4:3 live preview (480 px wide, 352 at minimum window size) with the head/shoulder guide outline and the "Live preview" tag; states Ready (Start) → "Capturing in 3…" (big number over the feed) → "Hold still…" (progress bar) → success (Done) / "Make sure you are in view and hold still" (Retry) / "The camera can't be read" (No picture, Retry). Cancel shows in every state except success. First launch and every Recalibrate (tray menu, Today, Settings, Stale banner) open this view and show the main window.

Needs from the monitor: `cancel_calibration()`, which ends a calibration in progress without changing the Baseline and returns to normal judging (Stale stays Stale); and capture progress (0..1) for the hold bar, derived from the existing countdown and capture timing.

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] Every state from the design is reachable with the real monitor and shows the design's copy
- [ ] Start begins the countdown; Retry restarts; Done closes the view; Cancel leaves the old Baseline untouched
- [ ] The feed only runs while the view is visible, and frames are still never kept
- [ ] The old `CalibrationWindow` is removed
- [ ] Tests: `cancel_calibration()` and capture progress through the Posture Monitor
