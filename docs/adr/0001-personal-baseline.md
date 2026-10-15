# Judge posture against a personal Baseline, not a universal rule

Posture is judged by comparing the User against their own Baseline, captured by sitting up straight during Calibration, rather than against fixed thresholds that apply to everyone (e.g. a maximum neck angle). Camera height and angle vary widely between setups (a laptop webcam looks up from below, an external one may look straight on), and bodies differ, so a universal rule would misjudge many Users from the first minute.

## Consequences

- The app cannot judge posture until a first Calibration has happened.
- A Baseline goes stale when the camera or seating changes, so the app must detect large changes in the camera view and ask the User to recalibrate.
- Sensitivity is expressed as "how far from the Baseline", not as absolute angles.
