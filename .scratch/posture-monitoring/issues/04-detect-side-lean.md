# 04: Detect Side Lean

**What to build:** Tilting the torso or head to the left or right, compared with the Baseline, counts as Side Lean. Side Lean triggers the Mirror exactly like Forward Lean. Switching between Forward Lean and Side Lean keeps counting as one stretch of Bad Posture, and when both apply at once the moment counts as Forward Lean.

**Blocked by:** 02

**Status:** ready-for-agent

- [ ] Side Lean to either side for 5 continuous seconds shows the Mirror; returning to Good Posture hides it
- [ ] Forward Lean for 3 s followed by Side Lean still shows the Mirror at 5 s
- [ ] A posture that is both Forward Lean and Side Lean is reported as Forward Lean
- [ ] Tests through the Posture Monitor cover left and right Side Lean, switching between kinds, and the combined case
