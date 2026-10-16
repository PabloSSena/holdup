# 12: Windows installer

**What to build:** Holdup is packaged with PyInstaller into an installer that installs and runs on a clean Windows machine with no Python present, with MediaPipe and its models bundled. This comes early to find packaging problems before the app grows.

**Blocked by:** 01

**Status:** ready-for-human

- [ ] A documented build command produces a Windows installer
- [ ] Installing on a clean Windows machine (no Python) and launching shows the tray icon and detects the User as present or Absent
- [x] MediaPipe models and Qt plugins are bundled and found at runtime
- [ ] The installed app writes its data to the User's local app-data folder, not the install folder
- [x] The build steps are recorded in the repo so they can be repeated

## Comments

**Done (build/posture-monitoring), partly.** Added `build.ps1` (PyInstaller onedir, then Inno Setup if installed), `installer.iss` (Inno Setup 6 script), a `build` extra in `pyproject.toml` (`pyinstaller>=6.10`, built with 6.22.3), a README section, and `*.spec` in `.gitignore` (`build/`, `dist/` were already there). No app code changed: `pose_detector.py` resolves the model via `Path(__file__).parent`, which PyInstaller maps to `_internal/holdup/models`, where `--add-data` puts it.

Verified: `build.ps1` builds `dist\Holdup\Holdup.exe` (~378 MB folder; MediaPipe drags in matplotlib, scipy, sounddevice). A copy run from outside the repo, with a temp working directory, stayed up for 75 s with no errors, and loaded `_internal\PySide6\plugins\platforms\qwindows.dll` and `_internal\mediapipe	asks\c\libmediapipe.dll`; a console build of the same spec printed MediaPipe's normal XNNPACK/inference logs, so the bundled model loads and detection runs.

Not verified:
- **Box 1**: no Inno Setup on the dev machine, so `HoldupSetup.exe` was never compiled; `installer.iss` is untested. Install it (`winget install JRSoftware.InnoSetup`) and rerun `build.ps1`.
- **Box 2**: no clean machine without Python was tried, and the tray icon/presence was not watched by eye.
- **Box 4**: the app writes no data yet (the Store is issue 03). The install folder is per-user but the app should still not write there: issue 03 should put the SQLite file in `%LOCALAPPDATA%\Holdup` (e.g. `QStandardPaths.AppLocalDataLocation` or `os.environ["LOCALAPPDATA"]`).

Found while testing (not packaging): on this machine `cv2.VideoCapture(0)` (default MSMF backend) took ~48 s to open, in dev and frozen alike, so the app sits with no detection for that long after launch. `cv2.CAP_DSHOW` opened in 0.4 s. Worth a fix in Camera Source (`CAP_DSHOW`, or env `OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS=0`); left alone here since another ticket owns that code.

Decisions for 13 (Start with Windows):
- Installed per-user (`PrivilegesRequired=lowest`) to `{localappdata}\Programs\Holdup\Holdup.exe`, so the login entry belongs in `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` (no admin needed). The app can register `sys.executable` when `sys.frozen` is set; in dev there is no exe to register.
- "On by default after install" can be done either by the app on first run, or by an `[Registry]` entry in `installer.iss` with `Flags: uninsdeletevalue` so uninstall removes it. Pick one so the Store and the Run key don't disagree.
- `AppId` in `installer.iss` is fixed; upgrades reinstall over the same folder.
