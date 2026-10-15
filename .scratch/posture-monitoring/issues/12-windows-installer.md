# 12: Windows installer

**What to build:** Holdup is packaged with PyInstaller into an installer that installs and runs on a clean Windows machine with no Python present, with MediaPipe and its models bundled. This comes early to find packaging problems before the app grows.

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] A documented build command produces a Windows installer
- [ ] Installing on a clean Windows machine (no Python) and launching shows the tray icon and detects the User as present or Absent
- [ ] MediaPipe models and Qt plugins are bundled and found at runtime
- [ ] The installed app writes its data to the User's local app-data folder, not the install folder
- [ ] The build steps are recorded in the repo so they can be repeated
