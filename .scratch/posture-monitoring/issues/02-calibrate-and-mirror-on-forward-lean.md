# 02: Calibrate, then see the Mirror on Forward Lean

**What to build:** On first launch the User is guided through Calibration: a window shows their live feed and an instruction to sit up straight, counts down 3 seconds, then captures their Baseline over about 2 seconds. From then on, when the User stays in Forward Lean (judged against the Baseline at Medium Sensitivity) for 5 continuous seconds, the Mirror appears in the bottom-left corner, always on top, showing only their live camera feed. It disappears as soon as they return to Good Posture. The Baseline lives in memory only for now.

**Blocked by:** 01

**Status:** ready-for-agent

- [x] Before the first Calibration, posture is not judged and the Mirror never appears
- [x] Calibration shows the live feed, the instruction and a countdown, then captures the Baseline
- [x] Calibration fails, and offers a retry, if no person is seen or the User moves too much during capture
- [x] Forward Lean for under 5 seconds shows no Mirror; at 5 continuous seconds the Mirror appears
- [x] Returning to Good Posture resets the 5-second count and hides the Mirror immediately
- [x] Becoming Absent hides the Mirror and resets the count
- [ ] The Mirror is frameless, always on top, fixed (not draggable) in the bottom-left corner of the primary screen, and shows only the plain live feed at a smooth rate while analysis stays at the low rate
- [x] Tests through the Posture Monitor cover: Calibration success and failure, the 5-second threshold (4.9 s vs 5 s), reset on Good Posture, and Mirror hidden on Absent

## Comments

**Done (worktree branch off build/posture-monitoring).** New: `src/holdup/posture_classifier.py` (Forward Lean judgement; every Sensitivity tuning number lives in `Limits` / `MEDIUM`), `src/holdup/windows.py` (`MirrorWindow`, `CalibrationWindow`). Changed: `posture_monitor.py` (Calibration, Forward Lean, Bad Posture timer, `mirror_visible`), `tray.py` (starts Calibration at launch, drives both windows), `tests/landmarks.py` (`leaning_forward(amount=0.3)`), `tests/test_posture_monitor.py`. 20 tests pass.

Verified on this machine: the real app (run through a smoke script that logs only text, never images) starts, the Calibration window appears, shows the live feed at 480x360, counts down 3-2-1, and, with nobody at the desk, fails and shows Retry. The Mirror window was checked programmatically: frameless, always on top, 320x240 at the bottom-left of the primary screen's work area, hidden again by `follow(False)`.

Box 7 is left unticked until checked by eye. Not verified: a successful Calibration with a real person, Forward Lean being detected with a real person (the `MEDIUM` limits are guesses on synthetic poses), the Mirror actually appearing over other windows, and the smoothness of its feed. Opening the camera took ~45 s on this machine (MSMF) in every run, before anything else shows. One run got no frames at all (MSMF "failed to start streaming", camera probably busy), which left Calibration stuck in its countdown because nothing was observed; issue 07 should cover that.

Decisions later tickets should know:
- **Posture Monitor API**: `begin_calibration()` (the Begin Calibration command; also hides the Mirror and resets the timer), `calibration_countdown()` (seconds before capture starts, 0 while capturing), `calibration_failed` (bool, cleared on begin), `mirror_visible` (bool, updated on each `observe()`). New `MonitorState`s: `CALIBRATING`, `GOOD_POSTURE`, `FORWARD_LEAN`.
- **Calibration**: 3 s countdown (observations ignored), then the UserSeen frames of the next 2 s are averaged into the Baseline. It ends on the first observation after the capture window. A `NoPerson` during capture fails it at once (no grace for detector flicker; revisit if real use shows spurious failures). A failure keeps any previous Baseline. "Moved too much" reuses the classifier: capture fails if any captured pose would count as Bad Posture against the first one, at Medium. Issue 04's Side Lean extends this for free; issue 05 should keep Calibration on Medium, not the User's Sensitivity.
- **Classifier**: `leans_forward(baseline, landmarks, limits=MEDIUM)`. Forward Lean = shoulders look more than 15% wider than in the Baseline (closer to the camera) OR the nose sank toward the shoulder line by more than 0.15 shoulder widths. OR rather than AND, so either sign alone counts; the tuning pass may change this. Issue 04 should turn it into a `classify()` returning Good/Forward/Side (Forward wins); issue 05 adds `LOW` / `HIGH` next to `MEDIUM`.
- **Bad Posture timer**: starts at the first Forward Lean observation; the Mirror is visible once `now - start >= 5 s`, judged at observation time. Any other observation resets it. Issue 04 must keep it running across Forward Lean and Side Lean; issue 10's Mirror count can hook where `mirror_visible` goes from False to True.
- **Frame pacing**: the tray now ticks every 33 ms but reads a camera frame only when analysis is due or a window shows the feed, so the Mirror and Calibration feeds are smooth while analysis stays at 0.4 s / 1 s. Calibrating uses the watching interval.
- **The Mirror is flipped left-right** like a real mirror (nothing drawn on it).
- **Shortcuts**: the Baseline is in memory only, so Calibration runs at every launch (issue 03 persists it and adds Recalibrate). Closing the Calibration window mid-way does not cancel it, and after a failed Calibration whose window was closed there is no way to retry until 03 adds Recalibrate.
