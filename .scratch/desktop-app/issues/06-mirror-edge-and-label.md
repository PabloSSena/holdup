# 06: Mirror edge and label

**What to build:** The Mirror from the design (the "Mirror" section): the same 320×240 frameless always-on-top window in the bottom-left, now with a 3 px inner edge and a small label in the bottom-left corner: amber #E2A45C with "Forward Lean" (label text #241808), periwinkle #A0A7E6 with "Side Lean" (label text #16183A). Edge and label follow the monitor's current lean while the Mirror shows. Nothing clickable; frames never kept.

**Blocked by:** none

**Status:** ready-for-agent

- [x] Forward Lean and Side Lean each show their edge colour and label
- [x] Switching between leans while the Mirror is up updates the edge and label
- [x] The Mirror still never takes focus and still hides on Good Posture or Pause
- [x] Test: a pure mapping from MonitorState to (colour, label), None for non-lean states

## Comments

**Done (worktree branch off build/posture-monitoring).** Changed: `windows.py` (`mirror_lean()`, a pure mapping from a monitor state to its edge colour and label, None for anything that is not a lean; `MirrorWindow.follow()` now also takes the state, paints a 3 px inner edge and shows a child label 10 px from the bottom-left corner), `tray.py` (the two `mirror.follow(...)` calls pass `monitor.state`). Tests: a new `tests/test_mirror_lean.py` (each lean's colour and label; every other state gives None). Full suite: 84 pass.

- The edge is painted over the feed, not a stylesheet border, so the frame still fills the 320×240 window and the edge sits on top of it as in the design.
- The label's text colour (#241808, #16183A) is looked up from the edge colour; the label text is the state's own name.
- Edge and label update on every analysis tick through `follow()`, so a switch between leans shows on the next tick. The Mirror is only visible in a lean state, so outside one the edge and label are simply cleared.
- Window flags are unchanged: still `WindowDoesNotAcceptFocus` and `WA_ShowWithoutActivating`; the label is a plain `QLabel` with nothing clickable.

Checked: rendered with a fake frame via `QWidget.grab()` for Forward Lean, then Side Lean, then back to Forward Lean on the same window (screenshots matched the design; the edge is exactly 3 px on each side); the window reported no focus and not active while shown, and hid on `follow(False, Good Posture)`. Not checked by hand: the Mirror appearing in the running app over a real desktop.
