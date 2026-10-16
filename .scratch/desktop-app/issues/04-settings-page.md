# 04: Settings page

**What to build:** The Settings page from the design (the "SETTINGS" block): Sensitivity segmented control (Low / Medium / High) with the Baseline zone bar (zone width 78 / 50 / 26 %) and the per-level description; Camera dropdown listing connected cameras (re-listed each time it opens; disabled "No camera found" state with "Plug in a camera and it shows up here.") with the Stale note; the Baseline row ("Captured today at 09:10" / "Captured Wed 14 Oct at 09:10", or the Stale text in warning ink, or "Needs a camera") with Recalibrate; Start with Windows toggle (only when frozen, as in the tray); the privacy card. Choosing a camera does exactly what the tray's `choose_camera` does: reuse it, don't copy it.

Needs from the monitor: when the Baseline was captured. Save it in the Store next to the Baseline on a successful calibration and expose it (e.g. `baseline_captured_at`, None for a Baseline saved before this change).

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] Changing Sensitivity here and in the tray menu stay in sync
- [ ] Choosing a camera switches the camera and makes the Baseline Stale, same as the tray
- [ ] Baseline row shows the captured time, the Stale text, or "Needs a camera"
- [ ] Start with Windows toggle reflects and changes the Run key (frozen build only; hidden from source)
- [ ] Tests: `baseline_captured_at` saved on calibration and surviving a restart, through the Posture Monitor
