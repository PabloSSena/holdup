# 02: Calibrate, then see the Mirror on Forward Lean

**What to build:** On first launch the User is guided through Calibration: a window shows their live feed and an instruction to sit up straight, counts down 3 seconds, then captures their Baseline over about 2 seconds. From then on, when the User stays in Forward Lean (judged against the Baseline at Medium Sensitivity) for 5 continuous seconds, the Mirror appears in the bottom-left corner, always on top, showing only their live camera feed. It disappears as soon as they return to Good Posture. The Baseline lives in memory only for now.

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] Before the first Calibration, posture is not judged and the Mirror never appears
- [ ] Calibration shows the live feed, the instruction and a countdown, then captures the Baseline
- [ ] Calibration fails, and offers a retry, if no person is seen or the User moves too much during capture
- [ ] Forward Lean for under 5 seconds shows no Mirror; at 5 continuous seconds the Mirror appears
- [ ] Returning to Good Posture resets the 5-second count and hides the Mirror immediately
- [ ] Becoming Absent hides the Mirror and resets the count
- [ ] The Mirror is frameless, always on top, fixed (not draggable) in the bottom-left corner of the primary screen, and shows only the plain live feed at a smooth rate while analysis stays at the low rate
- [ ] Tests through the Posture Monitor cover: Calibration success and failure, the 5-second threshold (4.9 s vs 5 s), reset on Good Posture, and Mirror hidden on Absent
