# 01: Watch the User: tray app that knows whether someone is there

**What to build:** Holdup starts as a Windows tray app, opens the Windows default camera, runs MediaPipe pose detection on frames, and feeds Observations (landmarks for the person closest to the camera, or "no person") into a first Posture Monitor. The tray icon shows whether the User is being seen or is Absent. This ticket lays the foundation every later ticket builds on: the Posture Monitor as a pure-logic core with an injected clock, the Camera Source and Pose Detector adapters, frame pacing, and the test harness (fake clock, synthetic landmark builders) that all later tests use.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] The app runs from the system tray with no main window and has a Quit item
- [ ] Sitting in front of the camera shows a "watching" tray icon; leaving the desk switches it to Absent, and coming back switches it back
- [ ] When several people are visible, only the person closest to the camera (largest in frame) is used
- [ ] Frames are analysed at about 2–3 per second while the User is present and about 1 per second while Absent; frames are discarded right after detection and never written to disk or logs
- [ ] The Posture Monitor has no Qt, camera or MediaPipe imports, and takes Observations and time from an injected clock
- [ ] Tests drive the Posture Monitor through its public inputs only, using synthetic landmark builders and a fake clock, and cover present ↔ Absent transitions
