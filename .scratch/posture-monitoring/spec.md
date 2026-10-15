# Spec: Posture monitoring (Holdup v1)

Status: ready-for-agent

## Problem Statement

People who spend hours at a computer gradually drift into Bad Posture: they lean toward the screen or slump to one side without noticing. By the time they notice, usually through back or neck pain, the habit is already set. Reminders on a timer ("sit up every 30 minutes") ignore what the person is actually doing, and posture apps that send video to the cloud are a privacy problem for something that watches you all day.

## Solution

Holdup is a Windows tray app that starts with Windows and quietly watches the User through their own camera. On first launch the User does a Calibration: they sit up straight once and that becomes their Baseline. From then on, whenever the User stays in Bad Posture (Forward Lean or Side Lean, judged against their Baseline with a chosen Sensitivity) for 5 seconds, the Mirror appears in the bottom-left corner of the screen showing their own live camera feed, so they can see themselves and correct. As soon as they return to Good Posture, the Mirror disappears.

The app stays out of the way. No warnings while the User is Absent, the camera is Camera Unavailable, the Baseline is Stale, or the User has chosen to Pause. If the camera view changes a lot, the app asks the User to recalibrate. Daily Stats show how much of their Watched Time was spent in Good Posture versus each kind of Bad Posture, and how often the Mirror appeared. Camera frames are analysed in memory and then discarded. Nothing is recorded or sent anywhere.

## User Stories

### Install and startup

1. As a User, I want Holdup to start automatically when Windows starts, so that I'm protected without remembering to launch it.
2. As a User, I want a tray-menu toggle to turn off starting with Windows, so that I can control what runs on my machine.
3. As a User, I want Holdup to live in the system tray with no main window, so that it doesn't clutter my taskbar.
4. As a User, I want a Quit item in the tray menu, so that I can fully stop the app when I want.
5. As a User, I want my Baseline, Sensitivity, chosen camera and startup preference to be remembered across restarts, so that I don't have to set things up again.

### Calibration

6. As a new User, I want to be guided through Calibration on first launch, so that the app knows what my Good Posture looks like.
7. As a User doing Calibration, I want to see my live camera feed and a clear instruction to sit up straight, so that I know what to do.
8. As a User doing Calibration, I want a short countdown before my Baseline is captured, so that I have time to settle into position.
9. As a User doing Calibration, I want to be told if Calibration failed (for example no person was visible or I moved too much) and be able to retry, so that I don't end up with a bad Baseline.
10. As a User, I want a Recalibrate item in the tray menu, so that I can capture a new Baseline whenever I change my setup.
11. As a User, I want no posture judging before my first Calibration is done, so that I never get warnings based on nothing.

### Stale Baseline

12. As a User who moved my laptop, changed chairs or adjusted my camera, I want the app to detect that the camera view has changed a lot, so that it doesn't judge me against a Baseline that no longer fits.
13. As a User with a Stale Baseline, I want a Windows notification asking me to recalibrate, so that I know why warnings stopped.
14. As a User with a Stale Baseline, I want the tray icon to show that state, so that I can see it at a glance if I missed the notification.
15. As a User with a Stale Baseline, I want posture judging to stop until I recalibrate, so that I never get false warnings.
16. As a User, I want switching to a different camera to make my Baseline Stale, so that I'm asked to recalibrate for the new viewpoint.

### Posture judgement

17. As a User, I want leaning toward the screen to count as Forward Lean, so that the most common Bad Posture is caught.
18. As a User, I want tilting my torso or head to the left or right to count as Side Lean, so that lopsided sitting is caught too.
19. As a User, I want posture judged against my own Baseline rather than a universal rule, so that my camera angle and body don't cause false warnings.
20. As a User, I want a Sensitivity setting (Low, Medium, High) in the tray menu, so that I can choose how strict the app is.
21. As a User, I want Sensitivity to default to Medium, so that the app is reasonable out of the box.
22. As a User, I want changing Sensitivity to take effect immediately, so that I can feel the difference right away.
23. As a User, I want only the person closest to the camera to be judged, so that people walking behind me don't affect my warnings.

### Mirror

24. As a User, I want the Mirror to appear only after I've been in Bad Posture for 5 continuous seconds, so that brief movements like reaching for a cup don't trigger it.
25. As a User, I want the 5-second count to restart whenever I return to Good Posture, so that only sustained Bad Posture triggers the Mirror.
26. As a User, I want switching between Forward Lean and Side Lean to keep counting as one stretch of Bad Posture, so that I'm not let off the hook by shifting.
27. As a User, I want the Mirror to show my live camera feed in the bottom-left corner of my screen, so that I can see my own posture and correct it.
28. As a User, I want the Mirror to be always on top of other windows, so that I see it whatever I'm doing.
29. As a User, I want the Mirror to show only the plain camera feed, so that it's simple and unambiguous.
30. As a User, I want the Mirror to stay visible for as long as I remain in Bad Posture, so that the reminder persists until I act.
31. As a User, I want the Mirror to disappear by itself as soon as I'm back in Good Posture, so that I don't have to dismiss anything.
32. As a User, I want the Mirror to be fixed in place (not draggable) in v1, so that its behaviour is predictable.
33. As a User, I want the Mirror to disappear if I become Absent, the camera becomes Camera Unavailable, the Baseline becomes Stale, or I Pause, so that it never lingers when it no longer applies.

### Absent and Camera Unavailable

34. As a User who steps away from my desk, I want the app to treat me as Absent and do nothing, so that it doesn't react to an empty chair.
35. As a User, I want Absent time excluded from my statistics, so that my numbers reflect only time I was actually sitting there.
36. As a User whose camera is unplugged, shuttered or in use by another app, I want the app to show Camera Unavailable on the tray icon and give no warnings, so that I understand why it's inactive.
37. As a User, I want the app to resume watching automatically when the camera becomes available again, so that I don't have to restart it.
38. As a User with several cameras, I want the Windows default camera to be used initially, so that it works without configuration.
39. As a User with several cameras, I want a Camera picker in the tray menu, so that I can choose which camera watches me.

### Pause

40. As a User about to join a video call or eat, I want to Pause for 30 minutes from the tray menu, so that I'm not warned while I'm deliberately not sitting at my desk normally.
41. As a User, I want Pause options of 30 minutes, 1 hour, or until resumed, so that I can match the length of the interruption.
42. As a User, I want watching to resume by itself when a timed Pause ends, so that I don't forget to turn it back on.
43. As a User, I want a Resume item in the tray menu while paused, so that I can end a Pause early.
44. As a User, I want the tray icon to show when I'm paused, so that I don't forget the app is inactive.
45. As a User, I want Paused time excluded from my statistics, so that pauses don't skew my numbers.

### Statistics

46. As a User, I want the app to record Daily Stats of how much Watched Time I spent in Good Posture, Forward Lean and Side Lean, so that I can see whether my posture is improving.
47. As a User, I want the Daily Stats to include how many times the Mirror appeared each day, so that I can see how often I needed reminding.
48. As a User, I want a Stats window from the tray menu showing today and the last 7 days, so that I can check my progress.
49. As a User, I want statistics shown as shares of Watched Time, so that "80% Good Posture" means 80% of the time I was actually being watched.
50. As a User, I want Stale Baseline and Camera Unavailable time excluded from my statistics, so that they only count time when posture was really judged.
51. As a User, I want my Daily Stats kept on my machine indefinitely, so that I can look back over long periods later.
52. As a User, I want a Clear statistics button, so that I can delete my data whenever I want.
53. As a User, I want days to split at local midnight, so that "today" matches my own clock.

### Privacy and resource use

54. As a privacy-conscious User, I want camera frames analysed in memory and discarded immediately, so that no image of me ever exists on disk.
55. As a privacy-conscious User, I want nothing sent over the network, so that my camera data never leaves my machine.
56. As a User, I want the stored Baseline and Daily Stats to contain only numbers, never images, so that the data I keep is harmless.
57. As a laptop User, I want the app to use little CPU and battery while running all day, so that it doesn't slow down my machine or drain my battery.

## Implementation Decisions

- **Stack** (ADR 0002): Python, MediaPipe pose detection, PySide6 (Qt) for the tray icon and windows, SQLite for persisted data, PyInstaller for the Windows installer. Windows only for v1.
- **Personal Baseline** (ADR 0001): every posture judgement compares the User's current landmarks with their Baseline. There are no absolute angle thresholds.

### Modules

- **Posture Monitor** (the core and the single test seam). Pure logic with no Qt, camera or MediaPipe imports. It takes three kinds of input:
  - **Observations**, one per analysed frame: either a set of body landmarks for the person closest to the camera, "no person", or "camera unavailable".
  - **Commands**: Pause(duration or until resumed), Resume, Begin Calibration, Set Sensitivity, Camera Changed, Clear Stats.
  - **Time**, from an injected clock.

  It exposes:
  - the current monitor state: one of Uncalibrated, Calibrating, Good Posture, Forward Lean, Side Lean, Absent, Camera Unavailable, Stale Baseline, Paused (Paused overlays whichever underlying state applies)
  - whether the Mirror should be visible
  - whether a recalibration prompt should be raised (once per Stale Baseline episode)
  - Daily Stats queries (today and a range of days)

  It owns the Bad Posture timer (5 seconds continuous, reset by Good Posture, Absent or any non-judging state; carried across switches between Forward Lean and Side Lean), the Mirror count (incremented each time the Mirror goes from hidden to visible), and the accumulation of Watched Time into Daily Stats.
- **Posture Classifier** (internal to Posture Monitor). It is given a Baseline, current landmarks and a Sensitivity, and returns Good Posture, Forward Lean or Side Lean.
  - Forward Lean is detected as the head and shoulders moving toward the camera and the head dropping forward relative to the shoulders, compared with the Baseline.
  - Side Lean is detected as a change in shoulder-line angle or head tilt compared with the Baseline.
  - When both apply, Forward Lean wins, so each moment is attributed to exactly one kind for Daily Stats.
  - Sensitivity maps Low, Medium and High to three sets of deviation limits. Exact values are tuned empirically, live in one place, and are not part of the public interface.
- **Calibration** (inside Posture Monitor). After Begin Calibration, it waits through a 3-second countdown, then averages landmarks over a short capture window (about 2 seconds) to form the Baseline. It fails if "no person" is observed or the landmarks vary too much during capture, and reports failure so the UI can offer a retry. A successful Calibration clears a Stale Baseline.
- **Stale Baseline detection** (inside Posture Monitor). It marks the Baseline Stale when the User's landmark geometry (overall scale and position in the frame) stays far from the Baseline for a sustained period, beyond what Forward Lean or Side Lean explains, or when a Camera Changed command arrives. Thresholds and duration are tunable constants.
- **Store** (behind a small interface used by Posture Monitor). A SQLite database in the User's local app-data folder. It holds:
  - the Baseline (landmark numbers)
  - settings: Sensitivity, chosen camera, start with Windows
  - Daily Stats rows keyed by local date: seconds in Good Posture, seconds in Forward Lean, seconds in Side Lean, Mirror count

  Watched Time is the sum of the three durations. Stats are kept indefinitely, and Clear Stats deletes all Daily Stats rows but keeps the Baseline and settings. No images are ever written.
- **Camera Source** (adapter). It opens the selected camera (initially the Windows default), lists the available cameras for the picker, and reports Camera Unavailable when frames can't be read. It retries periodically to detect when the camera comes back.
- **Pose Detector** (adapter). It wraps MediaPipe pose and turns a frame into an Observation. When several people are detected, it picks the person closest to the camera (the largest body in the frame). Frames are dropped right after detection.
- **Frame pacing**. About 2–3 analysed frames per second while judging, and about 1 per second while Absent, Camera Unavailable, Stale or Paused. While the Mirror is visible, the camera feed is displayed at a smooth rate, but analysis stays at the low rate.
- **Tray App** (Qt shell). It wires everything together and has a tray icon whose look reflects the monitor state: normal, Paused, Stale Baseline, Camera Unavailable, Uncalibrated. Menu: Pause (30 min / 1 hour / until resumed) or Resume, Recalibrate, Sensitivity (Low / Medium / High), Camera, Stats, Start with Windows (toggle), Quit. It raises a Windows notification when the Posture Monitor asks for recalibration.
- **Mirror window**. A frameless, always-on-top, non-draggable window anchored to the bottom-left corner of the primary screen. It shows only the live camera feed, and its visibility follows the Posture Monitor.
- **Calibration window**. Shows the live feed, the "sit up straight" instruction, the countdown, and success or failure with a retry option.
- **Stats window**. Shows today and the last 7 days: the share of Watched Time in Good Posture, Forward Lean and Side Lean, plus the Mirror count. It has a Clear statistics button with a confirmation.
- **Start with Windows**. Registers or unregisters the app to launch at user login, controlled by the tray toggle. It is on by default after install.

## Testing Decisions

- **One seam: the Posture Monitor.** Every automated test drives it only through its public inputs (Observations, Commands, injected clock) and checks only its public outputs (state, Mirror visibility, recalibration prompt, Daily Stats). Tests never reach into the Posture Classifier, Calibration or Stale Baseline detection directly, and never assert on threshold values. That way the classifier can be retuned without rewriting tests.
- **A good test** describes the User's behaviour over time and the expected outcome. For example:
  - Forward Lean for 4.9 s gives no Mirror; at 5 s the Mirror appears; on returning to Good Posture the Mirror hides, the Mirror count is 1, and those seconds appear as Forward Lean in today's Daily Stats.
  - Switching from Forward Lean to Side Lean at 3 s still shows the Mirror at 5 s.
  - Good Posture at 4 s resets the timer.
  - Absent, Paused, Stale and Camera Unavailable time add nothing to Watched Time.
  - A timed Pause ends by itself.
  - Camera Changed makes the Baseline Stale, raises exactly one recalibration prompt, and hides the Mirror.
  - A successful Calibration resumes judging.
  - A failed Calibration (no person during capture) reports failure and keeps the previous state.
  - Sensitivity High flags a small lean that Medium does not.
  - Stats split at local midnight.
  - Clear Stats empties Daily Stats but keeps the Baseline.
  - The Baseline, settings and stats survive re-creating the monitor on the same Store.
- **Test inputs**: synthetic landmark builders (an "upright" pose, and helpers that shift it forward or tilt it sideways by a given amount) plus a fake clock. Recorded landmark sequences from real sessions (numbers only, never images) may be added as fixtures to check that tuning is realistic.
- **Store in tests**: a real SQLite database in a temporary file, not a mock, so persistence and the day split are exercised for real.
- **Not automated**: Pose Detector accuracy, Camera Source, and the Qt windows and tray. These stay thin adapters and are checked by hand on a Windows machine with a real webcam (WSL can't reach the camera).
- **Prior art**: none. This is a new repo. These tests set the pattern.

## Out of Scope

- macOS and Linux.
- Bad Posture kinds other than Forward Lean and Side Lean (looking down at a laptop, sitting too close to the screen, slumping back).
- Drawing anything on the Mirror (labels, Baseline outline, landmarks), dragging it or resizing it.
- An adjustable Bad Posture delay (fixed at 5 seconds).
- Daily summary notifications, and statistics views beyond today plus the last 7 days.
- Fine-grained Sensitivity controls (angles or degrees).
- Recording, exporting or uploading any image or video, and any network access or telemetry.
- Watching more than one User at a time.

## Further Notes

- Glossary terms in this spec are defined in `CONTEXT.md`. Decisions are recorded in `docs/adr/0001-personal-baseline.md` and `docs/adr/0002-python-mediapipe-pyside.md`.
- The classifier thresholds and the Stale Baseline detection limits are the main tuning risk. Expect a hands-on tuning pass with real people and camera setups after the core works.
- "No images on disk" also applies to logs and crash reports: never log frames or write them in debug dumps.
