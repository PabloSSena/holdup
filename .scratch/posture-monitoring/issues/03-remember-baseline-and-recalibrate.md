# 03: Remember the Baseline and add Recalibrate

**What to build:** The Baseline and settings are saved in a local SQLite Store, so restarting Holdup resumes watching without a new Calibration. The tray menu gains a Recalibrate item that runs Calibration again and replaces the Baseline.

**Blocked by:** 02

**Status:** ready-for-agent

- [x] The Baseline (numbers only, never images) is stored in a SQLite database in the User's local app-data folder
- [x] After a restart, a previously calibrated User is watched immediately without Calibration
- [ ] Recalibrate in the tray menu runs Calibration; success replaces the stored Baseline, failure keeps the previous one
- [x] The Store sits behind a small interface used by the Posture Monitor, ready for settings and Daily Stats
- [x] Tests use a real SQLite database in a temporary file and check that the Baseline survives re-creating the Posture Monitor on the same Store

## Comments

**Done (worktree branch off build/posture-monitoring).** New: `src/holdup/store.py` (`Store`, `default_path()`), `tests/test_store.py` (4 tests). Changed: `posture_monitor.py` (`PostureMonitor(clock, store=None)`, `calibrated` property, the Baseline is loaded from the Store at start and saved on a successful Calibration), `tray.py` (opens the Store, calibrates only when no Baseline is stored, Recalibrate menu item). 24 tests pass.

Verified on this machine, with `LOCALAPPDATA` pointed at a temp folder: the app starts and creates `Holdup\holdup.db` there; a fresh launch shows the Calibration window; after storing a Baseline in the same database, a launch shows no Calibration window and keeps running.

Box 3 is left unticked until checked by hand: the logic (success replaces the stored Baseline, failure keeps it) is tested, but nobody has clicked Recalibrate in the tray menu yet. Not verified: a real person being judged right after a restart (the camera was held by other smoke runs, so DirectShow could not open it during my runs), and the Recalibrate item bringing the Calibration window to the front.

Decisions later tickets should know:
- **Store interface**: `Store(path=":memory:")` with `get(name, default=None)` / `set(name, value)`: named values saved as JSON in one `setting` table. The Baseline is `"baseline"` (a list of `[x, y, z, visibility]`). Issue 05 can use `get("sensitivity", "medium")`, 09 `"camera"`, 13 `"start_with_windows"` with no schema change. Issue 10 should add its own `daily_stats` table (`CREATE TABLE IF NOT EXISTS` in `Store.__init__`) with methods next to `get`/`set`, rather than squeezing rows into JSON.
- **File**: `%LOCALAPPDATA%\Holdup\holdup.db` (`default_path()`), created on first launch; each write commits at once. One connection, used on the Qt thread only.
- **Monitor and Store**: `PostureMonitor(clock, store=None)`; without a Store it uses an in-memory one, so existing tests and parallel tickets that build `PostureMonitor(clock=...)` keep working. The Posture Monitor owns all reads and writes; the Tray App only opens and closes the Store.
- **Recalibrate** = `monitor.begin_calibration()` plus showing the Calibration window; the window's Retry/Close and the "Calibrate at first launch only when `not monitor.calibrated`" rule are the only tray logic. Issue 08 should clear Stale on the same save path in `_end_calibration`.
