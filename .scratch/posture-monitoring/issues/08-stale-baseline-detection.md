# 08: Stale Baseline detection

**What to build:** When the camera view changes a lot (the laptop moved, a different chair or desk), the Baseline becomes Stale. Posture judging stops, the Mirror hides, the User gets one Windows notification asking them to recalibrate, and the tray icon shows the Stale state. A successful Calibration clears it.

**Blocked by:** 03

**Status:** ready-for-agent

- [x] A large, sustained change in the User's overall scale and position in the frame, beyond what Forward Lean or Side Lean explains, marks the Baseline Stale
- [x] Brief movements and ordinary Bad Posture never mark the Baseline Stale
- [x] While the Baseline is Stale, posture is not judged and the Mirror does not appear
- [ ] Exactly one Windows notification is raised per Stale episode; the tray icon shows the Stale state until recalibrated
- [x] A successful Calibration clears the Stale state and resumes judging
- [x] Detection thresholds and duration are tunable constants in one place
- [x] Tests through the Posture Monitor cover: a sustained geometry shift → Stale with exactly one prompt, an ordinary lean → not Stale, and recalibration clearing it

## Comments

**Done (worktree branch off build/posture-monitoring).** Changed: `src/holdup/posture_monitor.py` (new `MonitorState.STALE_BASELINE`, Stale detection, `take_recalibration_prompt()`, Stale cleared on a successful Calibration, Stale flag kept in the Store), `src/holdup/tray.py` (red tray icon for Stale, one `QSystemTrayIcon.showMessage` per prompt), `tests/test_posture_monitor.py` (9 new tests, 49 in all). A mutation pass (flipping each threshold, the clear, the persistence, the prompt and the idle rate) makes at least one new test fail every time.

Verified on this machine with `LOCALAPPDATA` in a scratch folder: the app starts; a first launch calibrated a real person and judged them for a few minutes without ever going Stale; a launch with a Stale flag pre-seeded in the database shows Stale Baseline and exits cleanly.

Box 4 is left unticked until checked by eye: the logic (exactly one prompt per episode, Stale state until recalibrated) is tested, but nobody has seen the Windows notification or the red icon yet. Not verified: a real camera move or chair change triggering Stale (the thresholds are guesses on synthetic poses).

Decisions later tickets should know:
- **Detection** = the shoulder width is outside 0.7x-1.8x of the Baseline width, or the shoulder midpoint moved more than 0.25 of the frame, continuously on every `UserSeen` frame for 30 s. Any frame inside those limits, Absent or Camera Unavailable restarts the 30 s. All four numbers (`STALE_AFTER`, `STALE_SCALE`, `STALE_SHIFT`) sit at the top of `posture_monitor.py`. A 25 degree Side Lean moves the shoulders ~0.19; a Forward Lean of +60% scale is still not Stale.
- **Stale wins over every other state** except Calibrating (also over Absent and Camera Unavailable), so the tray shows it until recalibrated. It uses the 1 s idle analysis rate, hides the Mirror and resets the Bad Posture timer.
- **Prompt**: `take_recalibration_prompt()` returns True once per episode (consumed on read); the tray checks it after each `observe()`.
- **Persists across restarts** (Store name `"baseline_stale"`), with no second prompt after a restart; judging against a wrong Baseline must not resume just because the app restarted. A failed Calibration leaves it Stale.
- **For 09 (Camera Changed)**: add `def camera_changed(self) -> None: self._make_stale()` to `PostureMonitor`; the tray must then check `take_recalibration_prompt()` after calling it (it is only checked after `observe()` today) or simply wait for the next tick. `_make_stale()` does not change `state`; the next `observe()` sets it. If called while Calibrating, the Calibration still succeeds and clears it.
- **For 10 (Daily Stats)**: Stale Baseline is not Watched Time; count `state` directly.
