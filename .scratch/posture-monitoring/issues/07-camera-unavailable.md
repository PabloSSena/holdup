# 07: Camera Unavailable

**What to build:** When the camera is unplugged, blocked by a privacy shutter, or held by another app, Holdup enters Camera Unavailable: no warnings, the Mirror is hidden, and the tray icon shows the state. When the camera comes back, watching resumes on its own.

**Blocked by:** 02

**Status:** ready-for-agent

- [ ] Unplugging the camera, or another app holding it, puts the app in Camera Unavailable without crashing
- [ ] Camera Unavailable is shown on the tray icon only; no notification is shown
- [ ] The Mirror hides on Camera Unavailable and the Bad Posture count resets
- [ ] The Camera Source retries periodically and watching resumes automatically when frames arrive again
- [ ] Camera Unavailable is a distinct state from Absent
- [ ] Tests through the Posture Monitor cover entering and leaving Camera Unavailable via "camera unavailable" Observations
