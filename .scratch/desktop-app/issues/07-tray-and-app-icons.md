# 07: Tray and app icons

**What to build:** The icons from the design (the "Tray icon & app icon" section). Tray: a coloured circle with a white glyph, painted with QPainter (no image files): Watching #3FA36B upright figure; Absent #8C948F outlined figure; Camera Unavailable #E07A2E figure struck through; Stale Baseline #D9534F figure with an alert badge; Paused #E3B53B pause bars; Calibrating #4C8BD6 three dots (a new tray state). Use the design's thicker 16 px shapes. App icon: rounded square #2F7D62 with the #F4F1EB figure, used as the window icon and as the exe and installer icon (generate a multi-size `.ico` once, check it in, and point `Holdup.spec` and `installer.iss` at it).

**Blocked by:** none

**Status:** ready-for-agent

- [ ] Each state shows its own glyph, readable without colour
- [ ] Calibrating gets its own tray icon
- [ ] Window icon, exe icon and installer icon use the app icon
- [ ] Test: every tray state maps to an icon (no state falls through)
