# 10: Record Daily Stats

**What to build:** While posture is being judged, Holdup records Daily Stats: seconds of Watched Time in Good Posture, Forward Lean and Side Lean, plus how many times the Mirror appeared. Days split at local midnight and data is kept indefinitely. Only judged time accumulates, so Paused, Absent, Stale Baseline and Camera Unavailable time never count.

**Blocked by:** 03, 04

**Status:** ready-for-agent

- [ ] Daily Stats rows are stored in the Store keyed by local date, holding Good Posture, Forward Lean and Side Lean seconds and the Mirror count; Watched Time is their sum
- [ ] The Mirror count increases by one each time the Mirror goes from hidden to visible
- [ ] Time in any non-judging state (Absent, Paused, Stale Baseline, Camera Unavailable, Uncalibrated, Calibrating) adds nothing
- [ ] Time crossing local midnight is split between the two days
- [ ] Stats survive restarts and are never deleted automatically
- [ ] The Posture Monitor exposes Daily Stats queries for today and a range of days
- [ ] Tests through the Posture Monitor with a real temporary SQLite database cover time attribution per kind, the Mirror count, exclusion of Absent time, and the midnight split
