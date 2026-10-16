# 06: Mirror edge and label

**What to build:** The Mirror from the design (the "Mirror" section): the same 320×240 frameless always-on-top window in the bottom-left, now with a 3 px inner edge and a small label in the bottom-left corner: amber #E2A45C with "Forward Lean" (label text #241808), periwinkle #A0A7E6 with "Side Lean" (label text #16183A). Edge and label follow the monitor's current lean while the Mirror shows. Nothing clickable; frames never kept.

**Blocked by:** none

**Status:** ready-for-agent

- [ ] Forward Lean and Side Lean each show their edge colour and label
- [ ] Switching between leans while the Mirror is up updates the edge and label
- [ ] The Mirror still never takes focus and still hides on Good Posture or Pause
- [ ] Test: a pure mapping from MonitorState to (colour, label), None for non-lean states
