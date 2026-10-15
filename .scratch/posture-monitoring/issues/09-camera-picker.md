# 09: Camera picker

**What to build:** Holdup uses the Windows default camera to start with. A Camera submenu in the tray lists available cameras so the User can choose another. The choice is remembered, and switching cameras makes the Baseline Stale so the User is asked to recalibrate for the new viewpoint.

**Blocked by:** 07, 08

**Status:** ready-for-agent

- [ ] The tray menu lists available cameras with the current one marked
- [ ] Choosing a different camera switches the feed and saves the choice in the Store
- [ ] Switching cameras makes the Baseline Stale (one notification, judging stops) until recalibrated
- [ ] If the saved camera is missing at startup, the app enters Camera Unavailable and keeps retrying
- [ ] Tests through the Posture Monitor cover the Camera Changed command producing a Stale Baseline
