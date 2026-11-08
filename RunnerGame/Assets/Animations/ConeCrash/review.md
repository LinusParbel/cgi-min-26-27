# Cone launch continuous-pursuit revision - 2026-11-07

The user rejected the hovering first cut and requested a continuously rising
rider, camera move to the officer, visible running jump, passing ticket slap,
falling officer and a camera that follows the rider. A follow-up requested a
shorter initial launch before revealing the officer.

Current combined preview: **v12**, 17 seconds: accepted v9 actor/camera motion,
approved soft-air flight audio, and the aerial city environment revision.
Motion and sound were approved before the live playtest. The new environment is
implemented and technically checked; final visual acceptance is pending review.

## Current renderer evidence

Repository-root paths, local ignored artifacts from the real game renderer:

- `docs/art/previews/cone-crash-v12.mp4`: current full 30 fps cut with approved sound.
- `docs/art/previews/cone-crash-v12-sheet.png`: current key-beat overview.
- `docs/art/previews/cone-crash-v12-frames/frame-0000.bmp` through `frame-0510.bmp`:
  current complete cut, staged with `--crash-distance 390` to include both plazas.
- `docs/art/previews/cone-city-v2-ticket-start.bmp`: aerial ticket shot at 8.5 s, preview distance 0.
- `docs/art/previews/cone-city-v2-ticket-later.bmp`: same shot, preview distance 250.
- `docs/art/previews/cone-city-v2-late-fog.bmp`: late flight at 16.5 s, preview distance 250.
- `docs/art/previews/cone-city-v2-launch-landmarks.bmp`: launch at 1.8 s, preview distance 390.
- `docs/art/previews/city-van-opening-check.bmp`: existing van opening at 3.7 s, with the city terrain installed.

The user's before images are preserved as `cone-background-user-fog.png` and
`cone-background-user-hollow.png` in the same preview folder. v1-v11 captures are
historical. v12 is the current complete recording. Audio is the approved WAV
muxed at scene time zero, not device-loopback capture.

## Aerial environment findings and correction

The first screenshot came from gray material fog against the cone scene's blue
clear color: distant landmarks became solid gray silhouettes instead of fading
into the background. RunnerLitMaterial now exposes FogColor, with the previous
gray default retained. SceneRenderer synchronizes each visible material to its
actual current sky color every frame, including pause/reset transitions.

The second screenshot exposed shallow 0.8 m facade modules and the limited street
strip. Complete building volumes now add over eight metres of depth, closed roofs,
parapets and small roof fixtures behind the existing facade art. Street rows and
plaza enclosures share those complete buildings. A batched surrounding district
adds four-sided buildings and paving beyond the street rows, reserving the full
Rathaus and clock-square footprints and enclosing wings across district seams.

Terrain extends beyond the fog range on both sides. The cone scene's road extends
before and behind the riding origin so no hard strip edge is exposed from above.
Terrain deliberately excludes the central road corridor: it cannot cap the van
scene's road opening. A real-renderer van capture verifies that opening remains.
Scenery is present before the cone contact, and the cloud staging has no separate
1.4 s visibility switch. No accepted actor clip, camera trajectory, gameplay rule,
shared model/atlas bytes or approved sound mix is changed by this revision.

Front building pieces and surrounding blocks are combined into static meshes.
The ticket shot uses 336 draws after batching, versus 624 in the initial version
of this environment. These are capture workload counts, not a frame-rate benchmark.
Geometry and source ownership are documented in Art/assets/street_city/README.md.

Keyframe review shows solid roofs and surrounding streets, consistent distant
fog, preserved landmark clearance and an intact van opening. Final full-speed
visual quality remains a user-review item. New rendering checks cover core depth,
closed roof surfaces, protected plazas and absence of terrain under the van hole.
Gameplay, animation, rendering and map metadata/shadow checks pass; runtime builds
with zero warnings/errors. Approved WAV source and installed hashes still match.

## What changed

Initial launch speed is half the previous value. The camera starts its move to
the officer at 2.05 s and reaches the run-up view at 2.8 s. The rider has only
only a short rise when the camera starts moving away, rather than the
previous long climb. They continue rising while the camera follows the officer.

Officer run-up uses the existing smooth, deforming ConeHat officer run, phased
from distance travelled. Root speed ramps up and down, then the shared gait
blends into the authored planted crouch before takeoff at 4.1 s. Flight follows
one ballistic interception solved to reach the rider's upper back at 7.3 s.
The lower rider flight now has a correspondingly lower officer arc: pre-contact
gravity is 3.2 m/s^2 rather than 8 m/s^2, so the officer approaches from below
instead of passing above the rider and coming back down. After the slap the
fall accelerates at 10 m/s^2. A brief push-off ramps sideways/backward/downward, after which gravity carries
the officer away. The rider never attaches to the officer or waits in the air.

The ticket follows the evaluated right palm before the slap. At 7.3 s it switches
continuously to the rider's evaluated back surface, offset 14 mm and oriented to
the surface normal. The officer naturally separates and withdraws the hand; the
paper stays attached. One brief slap replaces the repeated smoothing/pose hold.

Rider flight uses integrated smooth velocity ramps: continuous upward motion,
a gentler middle section that still rises at four metres per second, then
continued acceleration. Local flailing continues throughout; it no longer
blends into a frozen airborne pose. Camera eye and target blend through launch,
officer reveal, run, jump and moving close-up, then follow the rider upward.
There is no street-return cut. The view gradually pulls back for departure;
rider disappears at 16.2 s, followed by a small twinkle and sky hold.

The original measured front-wheel contact and shared initial pivot remain.
Actual collision X/Y/duck state blend into wheel/base contact over 0.35 s.
Rider and scooter separate continuously at 1.4 s. Scooter makes one continuous flip, tumbles onto its side and remains on the
street while the camera follows the launched rider. Ground support is measured
from all vertices of the actual shared body and wheel meshes, with their runtime
pivots. Every post-release pose is kept at least 2 mm above the road, rather than
blending a below-ground ballistic position into a fixed settling position.
First ground contact is about 2.62 s; the landing sound has been moved there.

## Continuous throw correction

Feedback on v8 identified a two-step flip/launch. The old tip eased to zero
angular speed before an independent upward trajectory began. The tip now keeps
rotating and begins its lift at 1.1 s, before release at 1.4 s. A Hermite flip
continues the same angle and angular speed. Rider flight inherits the evaluated
shared-pivot centre velocity; scooter flight inherits the pivot-origin velocity.
Their respective trajectories separate smoothly under the new rider ascent and
scooter gravity. Initial flight speed is reduced to retain the short first rise;
the middle still climbs at four metres per second. The launch sound starts with
the overlapping lift, and scooter landing sound follows the measured 2.62 s contact.

A release regression compares finite-difference velocities for origin, torso and
head points on both rider and scooter across 1.4 s. It also requires positive
upward carry and continuing angular motion, so a zero-speed pause cannot pass
merely because its position is continuous. All these checks pass.

## Source correction

Changing the officer bind pose to a later planted pose produced visible finger
and sleeve deformation in the moving close-up. The original frame-one bind
pose is restored. Four dark hip vertices accidentally bound to a nearby hand
were reweighted to pelvis in the editable source and re-exported. The runtime
clip, source and validation hash are aligned. No shared character atlas, run
clip, scooter, cone or van asset was modified.

## Verification

The animation suite checks exact wheel/base contact, release continuity, finite
poses/cameras, one palm/back intersection, continuing paper attachment and
separation in Rear/Side/Duck/low-Air contacts. A dense flight check rejects any
hover or stopped upward motion. Camera eye and target continuity are checked at
the reveal, jump, close-up, slap, follow and departure boundaries. The officer
must cover real run distance and reach running speed before takeoff. Dense
checks now reject any pre-slap torso overshoot above the rider, any scooter
vertex going through the road during the tumble, or a floating final rest pose.

The original implementation also passed gameplay, input, native Windows audio,
rendering contracts, route and map metadata/shadow harnesses, plus a solution
build. This revision changes scene staging, local clips, camera and sound cues;
the targeted animation checks and runtime build are rerun for the current cut.
Collision, score freezing, pause/focus/reset and pedestrian rules are unchanged.
Native audio transport retains the verified seek/pause/resume/reset path.

Audio now follows the run-up and 4.1 s jump, one 7.3 s paper slap, officer fall,
continuous air and 16.2 s twinkle. Run steps derive from the same distance curve
as gait playback. WAV is 17 s, mono PCM16 / 44.1 kHz, with no clipped samples.
See audio-cues.json and audio-sources.md. Existing character attribution and
licences remain in the source folders and RunnerGame/CREDITS.md.

## Review limits

Keyframes and the contact sheet establish staging/contact evidence, not final
normal-speed acting or listening quality. The latest recording is supplied for
that review. The user accepted v9 motion as good enough for now on 2026-11-07.
Flight audio revision 2 was subsequently approved for the live playtest. The motion is authored cartoon
physics, and clouds are simple code-native lobes. No general destruction or
physics system, new character identity, or other small-hazard ending is added.

## Reproduce

```powershell
dotnet run --project RunnerGame -- --cone-crash-preview
dotnet run --project RunnerGame -- --cone-crash-preview --capture docs/art/previews/cone-ticket-review.bmp --crash-time 7.3 --mute
dotnet run --project RunnerGame -- --cone-crash-preview --crash-film docs/art/previews/cone-review-frames --mute
```

For a later street district, add `--crash-distance 250` or `390` to a crash preview.
This option stages review scenery; it does not change normal gameplay.

Use .NET 10. This workstation's .NET 10 host is
`C:/Users/Tariq/AppData/Local/Microsoft/dotnet/dotnet.exe` (default PATH is .NET 8).
No commit or push was made.

## Flight sound feedback revision

The user was dissatisfied with the flying sound after accepting the motion.
Only flight components are replaced: the synthetic spring chirps, raw pulsing
wind and former departure/fall whooshes. The soft-air default uses smoothly
filtered, shaped gusts, a quieter bed, a dip around the paper slap and a distance
fade. Original non-flight stems reconstruct byte-for-byte before replacement;
no visual clip, camera, timing, collision or gameplay code is changed.

Current preview: docs/art/previews/cone-crash-v10.mp4, remuxed from the exact v9
renderer frames. Short launch auditions are cone-flight-air-launch.wav,
cone-flight-whistle-launch.wav and cone-flight-mixed-launch.wav in that same
ignored preview folder. Motion and sound acceptance are retained; the later city revision awaits visual review. audio-validation.json records duration, format, peak,
zero clipping and source-preservation evidence.

## Audio acceptance and live playtest

On 2026-11-07 the user approved the flight sound ("good add it to the game and
lets test it for real"). The runtime build contains the exact approved WAV: source
and installed SHA256 are BFCDDBC6FFD368797B211915FA86E57DA2CBDE59E569CAEEC5A829084185A99E.
Build passes with zero warnings/errors. A normal street-mode game was launched
with sound enabled, without capture, mute or crash-preview flags, for user playtesting.
Live gameplay feedback remains pending.
## 2026-11-08 visibility optimization

Camera/light visibility and 48-metre city groups are implemented. The full
17-second cone sequence was compared with culling enabled/disabled: all 511
frames at 30 Hz are pixel-identical, including shadows. Real-game matched shots
cover launch, officer run, ticket, departure and district wrap at 419/421 m.
The contact sheet was inspected; closed rooftops and the aerial city remain.
Actor clips, contact/camera timing and audio bytes are unchanged. Cinematic
animation still samples normally; only its draw submissions are filtered.
Release ticket-shot synchronized render median improved from 59.54 to 27.62 ms
in the paired local diagnostic; this is not measured live-game FPS.
See [visibility specification and validation](../../../../docs/superpowers/specs/2026-11-08-render-visibility.md).
User normal-speed playtest acceptance of this optimization is pending.
