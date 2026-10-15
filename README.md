# Holdup

A Windows tray app that watches your sitting posture through your own camera. When you lean forward or to one side for more than 5 seconds, a small Mirror of your live camera feed appears in the bottom-left corner of the screen, and it disappears as soon as you sit well again.

Camera frames are analysed in memory and discarded. Nothing is recorded or sent anywhere.

- Domain glossary: `CONTEXT.md`
- Decisions: `docs/adr/`
- Spec and tickets: `.scratch/posture-monitoring/`

## Development

Run on Windows-side Python 3.11 (not WSL: WSL can't reach the webcam).

Set up the virtualenv:

```
py -3.11 -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"
```

Run the app (it lives in the system tray; look in the tray overflow `^` if the icon is hidden, right-click it for Quit):

```
.venv\Scripts\python -m holdup
```

Run the tests:

```
.venv\Scripts\python -m pytest
```

The MediaPipe pose model (`src/holdup/models/pose_landmarker_lite.task`) is checked in, so the app never needs network access.
