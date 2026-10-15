# 13: Start with Windows

**What to build:** The installed app launches automatically when the User logs in to Windows. It is on by default after install, and a Start with Windows toggle in the tray menu turns it off or on. The choice is remembered.

**Blocked by:** 03, 12

**Status:** ready-for-agent

- [ ] After install, Holdup starts automatically at the next login
- [ ] The tray menu has a Start with Windows toggle reflecting the current state
- [ ] Turning the toggle off stops the app launching at login; turning it on restores it
- [ ] The preference is saved in the Store and stays consistent with what Windows actually does
- [ ] Verified by hand on a Windows machine with the installed build
