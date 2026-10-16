# 07: Tray and app icons

**What to build:** The icons from the design (the "Tray icon & app icon" section). Tray: a coloured circle with a white glyph, painted with QPainter (no image files): Watching #3FA36B upright figure; Absent #8C948F outlined figure; Camera Unavailable #E07A2E figure struck through; Stale Baseline #D9534F figure with an alert badge; Paused #E3B53B pause bars; Calibrating #4C8BD6 three dots (a new tray state). Use the design's thicker 16 px shapes. App icon: rounded square #2F7D62 with the #F4F1EB figure, used as the window icon and as the exe and installer icon (generate a multi-size `.ico` once, check it in, and point `Holdup.spec` and `installer.iss` at it).

**Blocked by:** none

**Status:** ready-for-agent

- [x] Each state shows its own glyph, readable without colour
- [x] Calibrating gets its own tray icon
- [ ] Window icon, exe icon and installer icon use the app icon
- [x] Test: every tray state maps to an icon (no state falls through)

## Comments

**Done (worktree branch off build/posture-monitoring).** Changed: new `src/holdup/icons.py` (`TRAY_COLORS`; `tray_glyph(state, paused)`, the state-to-icon mapping; `tray_icon(glyph)` and `app_icon()`, painted with QPainter on the design's 32x32 grid; and `write_ico()`), `tray.py` (the old `_dot_icon` is gone; the `icons` dict is built from `TRAY_COLORS`, `show_state()` picks the icon with `tray_glyph`, and `app.setWindowIcon(app_icon())` gives every window the app icon), new `assets/holdup.ico` (16/24/32/48/64/128/256, PNG entries), `build.ps1` (`--icon assets\holdup.ico`), `installer.iss` (`SetupIconFile=assets\holdup.ico`). There is no `Holdup.spec`: `build.ps1` passes PyInstaller's options on the command line. Tests: new `tests/test_tray_icons.py` (every Monitor State maps to a named icon, Paused wins over any state, each icon has its design colour). Full suite: 85 pass.

- Tray icons use the design's thicker 16 px shapes at every size (16 to 64 px pixmaps), as the issue asks. The Camera Unavailable slash is clipped to the circle: in the design SVG, the coloured gap's round caps stick out past the circle by about 2 px.
- Uncalibrated (no Baseline yet) shows the Calibrating icon. Before this change, it and Calibrating fell through to the Watching icon.
- `python -m holdup.icons assets/holdup.ico` regenerates the .ico after a design change. Qt's own ICO writer only stores one size, so `write_ico` writes the ICO header itself.

Checked: rendered each tray icon at 16 and 32 px on light and dark backgrounds, plus the app icon at 16/32/64/256, and compared them with the design (they match, apart from the clipped slash); Qt reads the .ico back; `python -m holdup` ran for 15 s without errors. Not checked: building the exe and installer (PyInstaller and Inno Setup were not run), so the exe and installer icons are untested and that box is left unticked. The window icon is set in code, but no window was opened by hand to look at it.
