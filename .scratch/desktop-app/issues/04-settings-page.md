# 04: Settings page

**What to build:** The Settings page from the design (the "SETTINGS" block): Sensitivity segmented control (Low / Medium / High) with the Baseline zone bar (zone width 78 / 50 / 26 %) and the per-level description; Camera dropdown listing connected cameras (re-listed each time it opens; disabled "No camera found" state with "Plug in a camera and it shows up here.") with the Stale note; the Baseline row ("Captured today at 09:10" / "Captured Wed 14 Oct at 09:10", or the Stale text in warning ink, or "Needs a camera") with Recalibrate; Start with Windows toggle (only when frozen, as in the tray); the privacy card. Choosing a camera does exactly what the tray's `choose_camera` does: reuse it, don't copy it.

Needs from the monitor: when the Baseline was captured. Save it in the Store next to the Baseline on a successful calibration and expose it (e.g. `baseline_captured_at`, None for a Baseline saved before this change).

**Blocked by:** 01

**Status:** ready-for-agent

- [x] Changing Sensitivity here and in the tray menu stay in sync
- [x] Choosing a camera switches the camera and makes the Baseline Stale, same as the tray
- [x] Baseline row shows the captured time, the Stale text, or "Needs a camera"
- [ ] Start with Windows toggle reflects and changes the Run key (frozen build only; hidden from source)
- [x] Tests: `baseline_captured_at` saved on calibration and surviving a restart, through the Posture Monitor

## Comments

**Done (worktree branch off build/posture-monitoring at a42c773).** `ui/settings.py` builds the page from the design's SETTINGS block: Sensitivity segments, the Baseline zone bar (78 / 50 / 26 %, done with layout stretch factors, no painting) and the per-level text; the Camera dropdown (`_CameraBox`, re-lists through `actions.camera_names` each time it opens and once per showing of the page, never on the tick; the tick leaves an open dropdown alone), the disabled "No camera found" state with its hint, the Stale note and the Baseline row with Recalibrate; the Start with Windows switch (only built when `actions.start_with_windows` is not None); the privacy card. Choosing a camera calls `actions.choose_camera`, the tray's own function. Icons (info, lock, chevron) are the design's SVGs, recoloured from `theme.THEMES` when the Windows theme changes. `posture_monitor.py`: new Store name `BASELINE_CAPTURED_AT` (ISO local time), written in `_end_calibration` on success, read by the new `baseline_captured_at` property (None for a Baseline saved before this). `theme.py`: rules appended for the new roles (`heading`, `strong`, `note`, `warning`, `caption`, `caption-strong`, `rule`, `privacy`, `track`, `zone`, `marker`, `small`, `switch`, `knob`, `#segments`, `QComboBox`). `tray.py`: one line, the tray menu re-reads Start with Windows when it opens, since the page can now change it. Tests: new `tests/test_settings.py` (5). Full suite: 96 pass.

- `baseline_text(captured_at, now, stale, has_camera, calibrated=True)` is the pure Baseline-row helper: "Needs a camera" wins over Stale, Stale over the time; "Not captured yet" without a Baseline; plain "Captured" for a Baseline without a time. Dates read "Wed 14 Oct" (day without a leading zero).
- "Needs a camera" follows the last camera listing (empty list), not the Camera Unavailable state: a camera held by another app is still listed.
- Stale is `monitor.state is STALE_BASELINE`, so the row shows the time again while recalibrating.
- A chosen camera that is unplugged shows the placeholder "Choose a camera" instead of pretending another one is in use.

Checked: `grab()` screenshots in light and dark, High Sensitivity with the switch off, the Stale state after choosing another camera through the page (state became Stale Baseline, warning ink text), and the no-camera state, all against the design; clicking the segments set the monitor's Sensitivity; the switch called `set_enabled` on a `StartWithWindows` with a fake Run key. Not checked: the dropdown popup's look and the "open dropdown is left alone" guard (popups do not open in this session, even a bare `QComboBox`), the real Run key from a frozen build (so its box stays unticked), and the tray menu's Sensitivity mark following a page change by hand (it goes through the tray's `set_sensitivity`).
