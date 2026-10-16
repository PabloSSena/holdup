# 09: Camera picker

**What to build:** Holdup uses the Windows default camera to start with. A Camera submenu in the tray lists available cameras so the User can choose another. The choice is remembered, and switching cameras makes the Baseline Stale so the User is asked to recalibrate for the new viewpoint.

**Blocked by:** 07, 08

**Status:** ready-for-agent

- [ ] The tray menu lists available cameras with the current one marked
- [ ] Choosing a different camera switches the feed and saves the choice in the Store
- [x] Switching cameras makes the Baseline Stale (one notification, judging stops) until recalibrated
- [ ] If the saved camera is missing at startup, the app enters Camera Unavailable and keeps retrying
- [x] Tests through the Posture Monitor cover the Camera Changed command producing a Stale Baseline

## Comments

**Done (build/posture-monitoring).** Changed: `posture_monitor.py` (`camera` property and `camera_changed(name)`: saves the name under Store name `"camera"` and makes the Baseline Stale if one exists; same camera again or no Baseline yet only saves), `camera_source.py` (takes a `locate()` callable that gives the DirectShow index on each open attempt, or None while the camera is missing, so Camera Unavailable retries every 3 s), `tray.py` (Camera submenu, rebuilt on each open from `QMediaDevices.videoInputs()`, current camera ticked; choosing one closes the feed, and the prompt is checked at once so the one notification shows straight away), 3 new tests (82 pass).

No saved choice = index 0, as before. The saved camera is matched by name; if it is missing, its index is None -> Camera Unavailable until it is back.

Verified: the app starts and detects with the real camera; `_camera_names()` lists `HD Pro Webcam C920` here.

Not verified (boxes 1, 2, 4 left for a hand check): the menu was not clicked by eye, and with one camera here no real switch or missing camera was tried. Known limit (`shortcut:` in `tray.py`): Qt's camera order is assumed to match DirectShow's; if the wrong camera opens on a multi-camera machine, enumerate DirectShow directly.
