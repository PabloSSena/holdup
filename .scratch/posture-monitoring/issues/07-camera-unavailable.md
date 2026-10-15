# 07: Camera Unavailable

**What to build:** When the camera is unplugged, blocked by a privacy shutter, or held by another app, Holdup enters Camera Unavailable: no warnings, the Mirror is hidden, and the tray icon shows the state. When the camera comes back, watching resumes on its own.

**Blocked by:** 02

**Status:** ready-for-agent

- [ ] Unplugging the camera, or another app holding it, puts the app in Camera Unavailable without crashing
- [x] Camera Unavailable is shown on the tray icon only; no notification is shown
- [x] The Mirror hides on Camera Unavailable and the Bad Posture count resets
- [x] The Camera Source retries periodically and watching resumes automatically when frames arrive again
- [x] Camera Unavailable is a distinct state from Absent
- [x] Tests through the Posture Monitor cover entering and leaving Camera Unavailable via "camera unavailable" Observations

## Comments

**Done (worktree branch off build/posture-monitoring).** Changed: `observation.py` (new `CameraUnavailable` Observation), `posture_monitor.py` (`MonitorState.CAMERA_UNAVAILABLE`, idle 1 s analysis rate, Calibration ends on it), `camera_source.py` (opens lazily, drops the handle on a failed read and reopens at most every 3 s), `tray.py` (an unreadable frame becomes a `CameraUnavailable` Observation; orange tray icon, tooltip "Holdup: Camera Unavailable"; no notification), `windows.py` (Calibration says the camera can't be read), `tests/test_posture_monitor.py` (+6 tests). 26 tests pass.

Verified on this machine: with another process holding the camera (DirectShow refuses a second opener, `isOpened()` is False), the real app went Calibrating -> Camera Unavailable within 0.4 s, retried every 3 s (a failed open costs ~0.06 s), and resumed watching on its own as soon as the holder released the camera; clean exit. A `CameraSource` probe showed the same recovery.

Box 1 is left unticked until the unplug case is checked by hand: only "held by another app" was exercised. Not verified: physically unplugging the camera or closing a privacy shutter (a shutter may still deliver black frames, which would read as Absent, not Camera Unavailable), whether a read on an unplugged DirectShow camera blocks the Qt thread, and the orange icon by eye (only the tooltip text was logged).

Decisions later tickets should know:
- **Camera Unavailable is immediate** on one unreadable frame, like Absent; the Mirror hides and the Bad Posture timer resets because it is not a Bad Posture state.
- **Calibration** ends as failed at once on a `CameraUnavailable` Observation (countdown or capture); a previous Baseline is kept. The User retries from the Calibration window (or Recalibrate, issue 03). It does not restart by itself when the camera returns.
- **Retry lives in `CameraSource`**: `read()` returns None while unreadable; after a failed read the handle is released and reopened at most every `RETRY_INTERVAL` (3 s). The camera now opens on the first `read()`, not at construction, so the tray appears before the camera is opened.
- **For 09 (Camera picker)**: switch cameras by closing the current `CameraSource` and constructing a new one with the chosen index (it is just `CameraSource(index)`); a missing saved camera then shows up as Camera Unavailable with the same 3 s retry, which covers box 4 of 09 for free. Index-based DirectShow ordering may differ from the Windows camera names; 09 needs a way to list names (OpenCV cannot).
- **For 10 (Daily Stats)**: Camera Unavailable is not Watched Time.
- **Shortcut**: camera open/read still runs on the Qt thread; a slow reopen would stall the tray for its duration.
