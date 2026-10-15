# 03: Remember the Baseline and add Recalibrate

**What to build:** The Baseline and settings are saved in a local SQLite Store, so restarting Holdup resumes watching without a new Calibration. The tray menu gains a Recalibrate item that runs Calibration again and replaces the Baseline.

**Blocked by:** 02

**Status:** ready-for-agent

- [ ] The Baseline (numbers only, never images) is stored in a SQLite database in the User's local app-data folder
- [ ] After a restart, a previously calibrated User is watched immediately without Calibration
- [ ] Recalibrate in the tray menu runs Calibration; success replaces the stored Baseline, failure keeps the previous one
- [ ] The Store sits behind a small interface used by the Posture Monitor, ready for settings and Daily Stats
- [ ] Tests use a real SQLite database in a temporary file and check that the Baseline survives re-creating the Posture Monitor on the same Store
