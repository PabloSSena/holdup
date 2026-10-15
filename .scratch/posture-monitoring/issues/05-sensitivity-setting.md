# 05: Sensitivity setting

**What to build:** The tray menu offers Sensitivity: Low, Medium or High, defaulting to Medium. It controls how far from the Baseline the User may sit before it counts as Bad Posture, for both Forward Lean and Side Lean. Changes take effect immediately and are remembered across restarts.

**Blocked by:** 03, 04

**Status:** ready-for-agent

- [ ] The tray menu shows Low / Medium / High with the current choice marked; the default is Medium
- [ ] Changing Sensitivity applies immediately to both Forward Lean and Side Lean
- [ ] The chosen Sensitivity is saved in the Store and restored on restart
- [ ] Threshold values live in one place and are not asserted on by tests
- [ ] Tests through the Posture Monitor show a small lean flagged at High but not at Medium, and a lean flagged at Medium but not at Low
