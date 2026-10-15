# 04: Detect Side Lean

**What to build:** Tilting the torso or head to the left or right, compared with the Baseline, counts as Side Lean. Side Lean triggers the Mirror exactly like Forward Lean. Switching between Forward Lean and Side Lean keeps counting as one stretch of Bad Posture, and when both apply at once the moment counts as Forward Lean.

**Blocked by:** 02

**Status:** ready-for-agent

- [x] Side Lean to either side for 5 continuous seconds shows the Mirror; returning to Good Posture hides it
- [x] Forward Lean for 3 s followed by Side Lean still shows the Mirror at 5 s
- [x] A posture that is both Forward Lean and Side Lean is reported as Forward Lean
- [x] Tests through the Posture Monitor cover left and right Side Lean, switching between kinds, and the combined case

## Comments

**Done (worktree branch off build/posture-monitoring).** Changed: `src/holdup/posture_classifier.py` (`leans_forward` replaced by `classify()` returning a `Posture`: `GOOD`, `FORWARD_LEAN`, `SIDE_LEAN`), `src/holdup/posture_monitor.py` (new `MonitorState.SIDE_LEAN`; the Bad Posture timer covers both kinds), `tests/landmarks.py` (`leaning_sideways(side, degrees=15, pose=None)`, `tilting_head(side, degrees=15)`), `tests/test_posture_monitor.py`. No tray or window changes were needed: the Mirror already follows `mirror_visible`. 28 tests pass.

Boxes are ticked on the strength of the tests through the Posture Monitor. Not verified: Side Lean with a real person and camera. The 8 degree limit is a guess on synthetic poses, as are the Forward Lean limits.

Decisions later tickets should know:
- **Side Lean** = the shoulder line (landmarks 11-12) OR the eye line (2-5, head tilt) has turned more than `MEDIUM.tilt` = 8 degrees from the Baseline, either way. One `tilt` limit covers both lines; the tuning pass may split it. The angle comes from cross/dot products, so it works whichever way MediaPipe orders left/right in the image (no wrap at 180 degrees).
- **Forward wins**: `classify()` checks Forward Lean first, so each moment is exactly one kind (issue 10 can count `state` directly).
- **`MonitorState` values match `Posture` values** ("Good Posture", "Forward Lean", "Side Lean"); the monitor maps with `MonitorState(posture.value)`. Keep them in step if either enum changes.
- **Timer**: runs while the state is Forward Lean or Side Lean; switching kinds does not restart it. Issue 10's Mirror count still hooks where `mirror_visible` goes False -> True.
- **Calibration** "moved too much" now also fails on a side lean during capture (any captured pose not judged Good against the first one, both ways, at Medium). Issue 05 should keep it on Medium and add `LOW` / `HIGH` next to `MEDIUM`, each with a `tilt` field.
