# 01: Watch the User: tray app that knows whether someone is there

**What to build:** Holdup starts as a Windows tray app, opens the Windows default camera, runs MediaPipe pose detection on frames, and feeds Observations (landmarks for the person closest to the camera, or "no person") into a first Posture Monitor. The tray icon shows whether the User is being seen or is Absent. This ticket lays the foundation every later ticket builds on: the Posture Monitor as a pure-logic core with an injected clock, the Camera Source and Pose Detector adapters, frame pacing, and the test harness (fake clock, synthetic landmark builders) that all later tests use.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [x] The app runs from the system tray with no main window and has a Quit item
- [ ] Sitting in front of the camera shows a "watching" tray icon; leaving the desk switches it to Absent, and coming back switches it back
- [x] When several people are visible, only the person closest to the camera (largest in frame) is used
- [x] Frames are analysed at about 2–3 per second while the User is present and about 1 per second while Absent; frames are discarded right after detection and never written to disk or logs
- [x] The Posture Monitor has no Qt, camera or MediaPipe imports, and takes Observations and time from an injected clock
- [x] Tests drive the Posture Monitor through its public inputs only, using synthetic landmark builders and a fake clock, and cover present ↔ Absent transitions

## Comments

**Done (build/posture-monitoring).** Layout: `src/holdup/` (`posture_monitor.py`, `observation.py`, `camera_source.py`, `pose_detector.py`, `tray.py`, `__main__.py`), `tests/` (`fakes.py` with `FakeClock`, `landmarks.py` with `upright()` / `upright_points(scale)`), `pyproject.toml`. 10 tests pass.

Box 2 is left unticked until checked by hand: the logic is implemented and tested, but nobody has watched the icon change yet. Verified by hand: the camera opens (640x480), MediaPipe detects the User in ~25 ms per frame, and `python -m holdup` starts and runs with no window and no errors. Not verified by eye: the tray icon itself (Windows put it in the hidden overflow), the green/grey switch when leaving and returning to the desk, and the several-people case with real people (covered only by a test of the selection function).

Decisions later tickets should know:
- **Observation types** (`holdup.observation`): `UserSeen(landmarks)` and `NoPerson()`; `Landmark` is a NamedTuple `(x, y, z, visibility)` in MediaPipe's 33-point layout. Add `CameraUnavailable` there in 07.
- **Closest person** = largest bounding box of landmarks clamped to the frame (`observation_from`), computed outside MediaPipe so it is testable.
- **Clock**: `PostureMonitor(clock=...)` takes a callable returning a local naive `datetime` (`datetime.now` in the app), so the local-midnight split in 10 can use it directly. `FakeClock.advance(seconds)` moves it.
- **State**: a present User is `MonitorState.UNCALIBRATED` (no Calibration exists yet); no person is `ABSENT`, also the state before any frame. Absent is immediate on one `NoPerson` frame (no grace period); revisit if detection flickers.
- **Frame pacing lives in the Posture Monitor**: `analysis_due()` (0.4 s while watching, 1 s while Absent). The tray polls every 100 ms and only reads and analyses a frame when due. Later non-judging states should use the idle interval. A clock jumping backwards makes analysis due rather than stalling.
- **MediaPipe** 1.x only has the Tasks API (no `mp.solutions`); the model `pose_landmarker_lite.task` is checked in and loaded as a buffer (issue 12 must bundle `src/holdup/models`).
- **Shortcuts**: an unreadable camera frame is silently skipped (07 replaces this); camera read and detection run on the Qt thread.
