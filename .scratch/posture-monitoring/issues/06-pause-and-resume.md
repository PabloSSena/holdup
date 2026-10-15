# 06: Pause and Resume

**What to build:** The User can Pause watching from the tray menu for 30 minutes, 1 hour, or until resumed. While Paused, the Mirror never appears and the tray icon shows the paused state. A timed Pause ends by itself; a Resume item ends any Pause early.

**Blocked by:** 02

**Status:** ready-for-agent

- [ ] The tray menu offers Pause for 30 minutes, 1 hour and until resumed, and shows Resume while Paused
- [ ] Pausing while the Mirror is visible hides it immediately
- [ ] No Mirror appears during a Pause, however long Bad Posture lasts
- [ ] A timed Pause ends automatically at the right time; Resume ends it early
- [ ] After a Pause ends, the 5-second Bad Posture count starts fresh
- [ ] The tray icon shows when the app is Paused
- [ ] Tests through the Posture Monitor, with the fake clock, cover timed expiry, early Resume and the Mirror hidden on Pause
