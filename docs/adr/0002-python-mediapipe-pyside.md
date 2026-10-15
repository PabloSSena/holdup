# Build with Python, MediaPipe and PySide6

Holdup is a Windows tray app built in Python, using MediaPipe for pose detection, PySide6 (Qt) for the tray icon, Mirror and Stats windows, SQLite for Daily Stats, and PyInstaller for packaging. Reliable pose detection is the riskiest part of the product and Python has the strongest computer-vision ecosystem, so we accept a clunkier installer in exchange for getting there fastest.

## Considered Options

- **Tauri (Rust) + MediaPipe in the webview**: smaller installer, but two languages to maintain.
- **Electron + MediaPipe JS**: familiar web stack, but the heaviest memory footprint for an app that runs all day.
- **.NET (C#) + an ONNX pose model**: most native on Windows, but the weakest computer-vision tooling.

## Consequences

- To save CPU and battery, frames are analysed at a low rate (about 2–3 per second while watching, about 1 per second while Absent). Only the visible Mirror needs a smooth feed.
- Development and testing must run on Windows-side Python, not inside WSL, because WSL cannot reach the webcam easily.
