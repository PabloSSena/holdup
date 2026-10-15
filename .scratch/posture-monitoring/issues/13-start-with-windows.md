# 13: Start with Windows

**What to build:** The installed app launches automatically when the User logs in to Windows. It is on by default after install, and a Start with Windows toggle in the tray menu turns it off or on. The choice is remembered.

**Blocked by:** 03, 12

**Status:** ready-for-agent

- [ ] After install, Holdup starts automatically at the next login
- [ ] The tray menu has a Start with Windows toggle reflecting the current state
- [ ] Turning the toggle off stops the app launching at login; turning it on restores it
- [x] The preference is saved in the Store and stays consistent with what Windows actually does
- [ ] Verified by hand on a Windows machine with the installed build

## Comments

**Done (worktree branch off build/posture-monitoring).** New: `src/holdup/start_with_windows.py` (`RunKey`, a thin `winreg` adapter for one value in `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`; `StartWithWindows(store, run_key, exe)` with `enabled`, `set_enabled(on)`, `apply()`), `tests/test_start_with_windows.py` (4 tests, fake Run key). Changed: `tray.py` (a checkable Start with Windows item before Quit, only when frozen), `installer.iss` (`[Registry]` entry that only removes the value on uninstall). 42 tests pass.

Owner of "on by default": **the app**. The Store holds `"start_with_windows"` (default `True`), and at every launch of the frozen app `apply()` writes `"<sys.executable>"` to the Run value `Holdup` or deletes it, so Windows follows the Store, and the entry follows the exe if it moves. The installer never writes the value (`ValueType: none` + `uninsdeletevalue`), so a reinstall cannot switch it back on against the User's choice; uninstall removes it. From source (`python -m holdup`) the item is hidden and the registry is never touched.

Verified: the real `RunKey` sets, deletes and re-deletes (no error) a value, using the name `HoldupTest`, which was deleted afterwards; no `Holdup` value was written to this machine's Run key.

Not verified (boxes 1-3 and 5 left for the hand check on an installed build): Inno Setup is still not installed here, so `HoldupSetup.exe` was not compiled. The registration happens on the first launch of the app, so the installer's "Start Holdup" postinstall box (on by default) is what makes it start at the next login; if the User unticks it, autostart begins only after they launch Holdup once. Not handled: turning Holdup off in Task Manager's Startup tab (Windows keeps that in `StartupApproved`, not the Run key), so the tray toggle would still show it ticked.
