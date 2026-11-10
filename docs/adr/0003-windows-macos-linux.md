# Ship for Windows, macOS and Linux from one codebase

Holdup started as a Windows-only app (see 0002). The stack is cross-platform (Python, MediaPipe, PySide6, PyInstaller), so macOS and Linux need only a few OS-specific seams, not a port. They are: where the Store lives, the camera capture backend, the start-at-login entry, and reading the display language. Each seam is chosen by `sys.platform` in the module that owns it, and takes the platform as a parameter so tests cover every OS from any machine.

## Decisions

- **Packages**: Windows keeps the per-user Inno Setup installer. macOS gets a drag-to-Applications `.dmg`, one per architecture (Apple Silicon, Intel). Linux gets an AppImage (any distribution) and a `.deb` (Ubuntu, Debian). Asset names carry no version, so the website can link to `releases/latest/download/<name>`.
- **One release, all OSes**: a `v*` tag builds every package on its own GitHub runner. The Release is created only after all of them pass, so the site never links to a missing file.
- **Unsigned**: no Apple Developer ID or Windows code-signing certificate (both cost money every year). macOS builds are ad-hoc signed, so users approve them once in Privacy & Security, as Windows users do with SmartScreen.
- **Start at login**: Windows uses the Run key, macOS a LaunchAgent and Linux an XDG autostart file. They share one saved preference, still stored under the name `start_with_windows` so existing choices carry over. In an AppImage, the AppImage file is registered, not the temporary mount it runs from.
- **XWayland on Linux**: Wayland doesn't let an app place its own window or keep it on top, which the Mirror needs. Holdup asks Qt for the X11 platform, which runs under XWayland on Wayland desktops.
- **Intel Macs stay on mediapipe 0.10.21**: later mediapipe releases ship arm64-only Mac wheels. The `mediapipe>=0.10.20` requirement lets pip pick 0.10.21 on Intel and the newest release elsewhere. When 0.10.21 stops working with the rest of the stack, the Intel build will be dropped.

## Consequences

- The tray icon on GNOME needs the AppIndicator extension; the AppImage needs `libfuse2` on the User's machine.
- The camera list still assumes Qt lists cameras in the capture backend's order (DirectShow, AVFoundation, V4L2), as it did on Windows.
- Development no longer has to happen on Windows, though the Windows installer can only be built there.
