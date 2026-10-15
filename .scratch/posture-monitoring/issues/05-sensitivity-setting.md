# 05: Sensitivity setting

**What to build:** The tray menu offers Sensitivity: Low, Medium or High, defaulting to Medium. It controls how far from the Baseline the User may sit before it counts as Bad Posture, for both Forward Lean and Side Lean. Changes take effect immediately and are remembered across restarts.

**Blocked by:** 03, 04

**Status:** ready-for-agent

- [x] The tray menu shows Low / Medium / High with the current choice marked; the default is Medium
- [x] Changing Sensitivity applies immediately to both Forward Lean and Side Lean
- [x] The chosen Sensitivity is saved in the Store and restored on restart
- [x] Threshold values live in one place and are not asserted on by tests
- [x] Tests through the Posture Monitor show a small lean flagged at High but not at Medium, and a lean flagged at Medium but not at Low

## Comments

**Done (worktree branch off build/posture-monitoring).** Changed: `src/holdup/posture_classifier.py` (`Sensitivity` enum `LOW`/`MEDIUM`/`HIGH` with values "Low"/"Medium"/"High"; `LOW` and `HIGH` `Limits` next to `MEDIUM`; `LIMITS` maps each Sensitivity to its Limits), `src/holdup/posture_monitor.py` (`monitor.sensitivity` property: read from the Store at start, default Medium; setting it saves to the Store and applies on the next `observe()`), `src/holdup/tray.py` (Sensitivity submenu between Recalibrate and Quit, exclusive checkable Low / Medium / High), `tests/test_posture_monitor.py` (+5 tests). 43 tests pass.

Verified on this machine with `LOCALAPPDATA` pointed at a scratch folder: a smoke script started the real app and read the tray menu: Recalibrate, Sensitivity (Low / Medium checked / High), Quit. It clicked High, and on the next launch High was checked. Not verified: the menu by eye, and whether the Low / High limits feel right with a real person. They are guesses on synthetic poses like Medium (Low: 25% / 0.25 / 13 degrees; High: 8% / 0.08 / 5 degrees), and need the hands-on tuning pass.

Decisions later tickets should know:
- **Store**: `"sensitivity"` holds the enum value string ("Low", "Medium", "High"). An unknown or missing value reads as Medium.
- **Calibration stays at Medium**: the "moved too much" check still calls `classify()` with its default `MEDIUM`, whatever the User's Sensitivity.
- **Changing Sensitivity does not reset the Bad Posture timer**: a lean already being timed keeps its start time if it is still Bad Posture under the new limits, and the timer resets on the next observation if it is not.
- **Tests** pick leans of different sizes (`leaning_forward(0.1 / 0.2)`, `leaning_sideways(degrees=6 / 10)`) that fall between the levels. They never assert the numbers themselves. A tuning pass that moves a limit past one of these leans must also pick new leans.
