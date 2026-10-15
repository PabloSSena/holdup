# 08: Stale Baseline detection

**What to build:** When the camera view changes a lot (the laptop moved, a different chair or desk), the Baseline becomes Stale. Posture judging stops, the Mirror hides, the User gets one Windows notification asking them to recalibrate, and the tray icon shows the Stale state. A successful Calibration clears it.

**Blocked by:** 03

**Status:** ready-for-agent

- [ ] A large, sustained change in the User's overall scale and position in the frame, beyond what Forward Lean or Side Lean explains, marks the Baseline Stale
- [ ] Brief movements and ordinary Bad Posture never mark the Baseline Stale
- [ ] While the Baseline is Stale, posture is not judged and the Mirror does not appear
- [ ] Exactly one Windows notification is raised per Stale episode; the tray icon shows the Stale state until recalibrated
- [ ] A successful Calibration clears the Stale state and resumes judging
- [ ] Detection thresholds and duration are tunable constants in one place
- [ ] Tests through the Posture Monitor cover: a sustained geometry shift → Stale with exactly one prompt, an ordinary lean → not Stale, and recalibration clearing it
