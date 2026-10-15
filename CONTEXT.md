# Holdup

A Windows desktop app that watches a person at their computer through their own camera and warns them when their sitting posture degrades. Camera frames never leave the machine and are never stored.

## Language

### People

**User**:
The single person sitting in front of the computer whose posture is being watched: the one closest to the camera. Anyone else in the frame is ignored.
_Avoid_: Person, customer, subject

### Posture

**Baseline**:
The User's own Good Posture, captured once by sitting up straight. Every posture judgement is a comparison against it.
_Avoid_: Reference pose, default position

**Calibration**:
The act of capturing a new Baseline. Happens at first launch, on demand, or when the app detects a Stale Baseline.
_Avoid_: Setup, training

**Stale Baseline**:
A Baseline that no longer matches the User's setup because the camera view has changed a lot (camera moved, different chair or desk, a different camera chosen). Posture is not judged until the User recalibrates.
_Avoid_: Drift, invalid baseline

**Sensitivity**:
How far from the Baseline the User may sit before it counts as Bad Posture: Low, Medium or High. One setting covers both kinds of Bad Posture.
_Avoid_: Threshold, strictness, tolerance

**Good Posture**:
Sitting close enough to the Baseline.
_Avoid_: Upright, neutral, correct posture

**Bad Posture**:
Sitting measurably away from the Baseline in a way the app warns about. Comes in two kinds: Forward Lean and Side Lean.
_Avoid_: Slouch, bent, hunched

**Forward Lean**:
A Bad Posture where the torso or head has moved toward the screen compared to the Baseline.
_Avoid_: Bending forward, hunching

**Side Lean**:
A Bad Posture where the torso or head has tilted to the left or right compared to the Baseline.
_Avoid_: Tilt, leaning sideways

**Absent**:
The state where no User is in front of the camera. Posture is not judged and no warning is shown.
_Avoid_: Away, idle

**Camera Unavailable**:
The state where the camera itself cannot be read (unplugged, shutter closed, held by another app). Distinct from Absent: the app cannot see, rather than sees nobody.
_Avoid_: Offline, disconnected, Absent

**Watched Time**:
Time during which posture is actually being judged: the User is present, not Paused, the camera is available and the Baseline is not Stale. Every statistic is a share of Watched Time.
_Avoid_: Active time, session time, uptime

### Warning

**Mirror**:
The always-on-top window in the bottom-left corner of the screen showing only the User's live camera feed. It appears when Bad Posture has lasted long enough and disappears once Good Posture returns.
_Avoid_: Overlay, popup, alert, notification

**Pause**:
A period during which the User has chosen to stop being watched (30 minutes, 1 hour, or until resumed). The Mirror never appears while paused.
_Avoid_: Snooze, mute, disable

### Statistics

**Daily Stats**:
The per-day record of Watched Time spent in Good Posture, Forward Lean and Side Lean, plus how many times the Mirror appeared. Numbers only, never images; kept on the User's machine indefinitely.
_Avoid_: History, report, analytics
