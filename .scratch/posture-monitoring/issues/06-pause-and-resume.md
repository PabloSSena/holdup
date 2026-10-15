# 06: Pause and Resume

**What to build:** The User can Pause watching from the tray menu for 30 minutes, 1 hour, or until resumed. While Paused, the Mirror never appears and the tray icon shows the paused state. A timed Pause ends by itself; a Resume item ends any Pause early.

**Blocked by:** 02

**Status:** ready-for-agent

- [x] The tray menu offers Pause for 30 minutes, 1 hour and until resumed, and shows Resume while Paused
- [x] Pausing while the Mirror is visible hides it immediately
- [x] No Mirror appears during a Pause, however long Bad Posture lasts
- [x] A timed Pause ends automatically at the right time; Resume ends it early
- [x] After a Pause ends, the 5-second Bad Posture count starts fresh
- [ ] The tray icon shows when the app is Paused
- [x] Tests through the Posture Monitor, with the fake clock, cover timed expiry, early Resume and the Mirror hidden on Pause

## Comments

**Done (worktree branch off build/posture-monitoring).** Changed: `posture_monitor.py` (`pause()`, `resume()`, `paused`; Paused suppresses the Bad Posture timer and uses the idle analysis rate), `tray.py` (menu items, amber paused icon, "Holdup: Paused" tooltip), `tests/test_posture_monitor.py` (7 new tests). 27 tests pass.

Verified: a smoke run of the real tray app (camera replaced by a blank frame because the real camera blocked on open, probably held by another process) built the menu, showed the three Pause items, switched to Resume plus "Holdup: Paused" after Pause for 30 minutes, stayed paused across ticks, and switched back after Resume. Box 6 is left unticked until checked by eye: the amber icon was set but not seen (Windows hides it in the overflow). Not verified: a timed Pause expiring in the real app (only with the fake clock), and the Mirror being hidden by a Pause on screen.

Decisions later tickets should know:
- **API**: `pause(duration: timedelta | None = None)` (None = until resumed), `resume()`, and the property `paused`, which reads the clock, so a timed Pause ends by itself with no tick or observation needed. Pausing again replaces the current Pause. Pause is not persisted: a restart is never Paused.
- **Paused overlays the state**: `state` keeps tracking the underlying state (Absent, Good Posture, Forward Lean...) while Paused; only the Mirror and the Bad Posture timer are suppressed. Check `paused` first. Issue 07/04 states need nothing extra: anything Bad Posture is suppressed by `and not self.paused` on the `bad` line.
- **Issue 10**: Watched Time must exclude any observation where `monitor.paused` is true (the underlying `state` still says Good Posture / Forward Lean while Paused, so counting by `state` alone would be wrong).
- **Frame pacing**: Paused uses the 1 s idle rate. This also applies to a Calibration started while Paused (fewer frames captured); issue 03 should decide whether Recalibrate ends a Pause.
- **Tray**: `show_state()` refreshes the icon, tooltip and Pause/Resume visibility; it runs on every analysed frame (once a second while Paused), so the icon changes back within ~1 s of a timed Pause ending. Icon priority: Paused over Absent over watching. Issue 07: while frames can't be read, `show_state()` isn't reached, so the expiry isn't shown until frames come back; call `show_state()` on the Camera Unavailable path too.
- **Clock**: a timed Pause stores its end time; if the clock jumps backwards the Pause lasts longer by that much.
