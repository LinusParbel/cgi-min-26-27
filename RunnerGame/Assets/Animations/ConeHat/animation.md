# Cone hat opening animation

## Status

Concept ID: `cone_hat`. User selected the cone-hat premise on 2026-11-02.
**Animation and audio are not implemented. All acceptance criteria are pending.**
This is the authoritative scene specification; the storyboard illustrates it.
The 12-second timing, camera staging and playback rules are proposed defaults
for review, not decisions already approved by choosing the premise.

[Storyboard](storyboard.svg) · [Folder convention](../README.md) ·
[Other ideas](../../../Art/ANIMATION_IDEAS.md)

## Intent and humour

The rider takes a traffic cone, wears it as a hat and gets caught by an
Ordnungsamt officer. A guilty pause turns into a frantic escape on the scooter.
The officer takes a petty offence absurdly seriously. The contrast between
slow cone removal and sudden sprint carries the joke; the mount fumble and
ill-timed beep are the payoff. Body language must tell the story when muted.

## Storyboard

Target: 12 seconds of active playback, excluding pauses. The storyboard uses
schematic figures, not the final character appearance or verified world positions.

| Shot | Time | Action and acting | Camera | Sound |
|---|---|---|---|---|
| S01 | 0.00–1.50 s | Casual walk toward cone; scooter waits a few steps ahead. | Wide three-quarter shot establishes rider, cone, scooter and escape direction. | Ambience, slow footsteps. |
| S02 | 1.50–3.00 s | Bend, lift cone with both hands, put broad opening over head; proud swagger. | Medium full-body view keeps hands, cone and silhouette visible. | Handling scrape, steps. |
| S03 | 3.00–4.25 s | Officer interrupts; rider freezes, then turns toward officer. | Reveal officer along rider's eyeline; preserve screen direction. | One throat-clear or short call. |
| S04 | 4.25–5.00 s | Awkward eye contact; shoulders sag. | Hold two-shot or readable reverse angle. | Ambience only for at least 0.50 s. |
| S05 | 5.00–6.50 s | Slowly remove cone, attempt innocent expression, release it beside rider. | Medium view shows removal, release and first ground contact. | Plastic clatter on contact. |
| S06 | 6.50–8.00 s | Cone rocks; rider abruptly sprints to scooter; officer reacts and follows. | Wider follow shot keeps destination visible. | Fast steps; optional “Stehenbleiben!”. |
| S07 | 8.00–10.00 s | Catch handlebar, fumble mounting, plant feet, settle into riding pose. | Side three-quarter angle makes fumble and successful mount distinct. | One badly timed beep during fumble. |
| S08 | 10.00–12.00 s | Pull away; officer runs behind; blend camera into gameplay. | Finish at regular chase view without teleport or framing snap. | Acceleration, receding steps, continuous ambience. |

Check the actual cone opening and head fit before committing to staging.
A view through the opening is optional; use a readable head turn and silhouette
if the geometry hides the face. Do not depend on dialogue to explain the joke.

## Assets and staging

| Role | Shared runtime folder | New work |
|---|---|---|
| Rider | `Assets/Models/Charakter/ScooterRider/` | Walk, lift, swagger, freeze, removal, sprint and mount actions. |
| Officer | `Assets/Models/Charakter/Ordnungsamt/` | Idle, interruption and reaction; reuse run cycle where suitable. |
| Scooter | `Assets/Models/Fahrzeug/ScooterVoi/` | Parked staging, hand/handlebar and foot/deck contacts, takeoff. |
| Cone | `Assets/Models/Baustelle/Leitkegel/` | Choose 50 or 75 variant after fit check; attachments, release, rocking. |

Stage on flat unobstructed ground, with a short approach and sprint path.
The released cone must stay outside the riding corridor and must not become
a gameplay obstacle. Preserve existing character identity, textures and scale.

Proposed scope: original street mode, HannoverPedestrianBlockout and
HannoverPublicRealm. Exact stage anchors and camera clearance must be checked
in each environment; the storyboard does not establish those placements.

## Proposed playback and handoff contract

These are defaults awaiting review, not existing engine behaviour.

1. Ready remains idle until Enter or Space starts the intro.
2. During playback, movement/jump/duck cannot affect gameplay. Distance, score,
   coins, hazard progression and damage remain at their initial values.
3. A new Enter/Space press after releasing the triggering press skips to the
   normal handoff. Holding Start must not immediately skip the scene.
4. Esc or focus loss pauses animation time and audio together. Focus return
   alone does not resume; Enter resumes only and cannot also skip on that press.
   Esc toggles pause/resume while focused; other paused inputs do not skip.
5. R stops audio, clears scene objects and resets to Ready. The next Start
   replays the intro; skipping remains available every time.
6. Natural completion and skip invoke the same handoff exactly once: rider
   mounted, route aligned, cone outside corridor, normal chase camera, clean
   score/distance and normal initial gameplay speed (currently 12 m/s).
7. Proposed default: officer remains visibly behind the player during the run,
   independently of the damage/pursuit timer, including after its clean escape
   interval. This changes the current renderer, which normally shows the officer
   only during timed pursuit or capture. Confirm this visual behaviour before
   implementation. Do not count the intro as a
   first collision or start the second-hit capture timer; preserve existing
   first-hit/second-hit gameplay rules.
8. Do not carry intro-only input or animation time into gameplay. No duplicate
   actors, stale cues or lingering sounds may survive skip or restart.

Exact world placements and officer spacing are implementation decisions,
subject to the visual continuity and clear-route acceptance criteria.

## Audio requirements

Required cues: ambience, walking/running steps, officer interruption, cone
handling/contact, mount beep and takeoff. The German spoken line is optional.

- Trigger sound from named action events, not render-frame counts.
- Impact follows ground contact; beep follows mount fumble; steps follow footfalls.
- No step loop during the freeze. Leave the awkward pause free of music stings.
- Pause, resume, skip and restart cannot replay old cues or leave orphan loops.
- Respect mute/volume settings; unavailable optional speech cannot block playback.
- Record source, licence and attribution for every delivered sound.
- Check actual capture synchronisation, not just the authored event list.

## Acceptance criteria

Every criterion is pending. A storyboard or unit test alone cannot prove acting,
contact quality or final sound synchronisation.

| ID | Requirement | Evidence needed |
|---|---|---|
| AC01 | S01–S08 occur in order; cone misuse, discovery, guilty reaction and escape read with muted audio. | Full muted capture reviewed against shots. |
| AC02 | Cut targets 12 s, draft tolerance ±0.5 s; eye-contact pause lasts at least 0.50 s. | Playback timestamps and full capture. |
| AC03 | Walking/sprinting have planted feet; rider bends and reaches to lift cone. No rigid whole-body sliding substitutes for actions. | Full-body and side views of S01, S02, S06. |
| AC04 | Hands contact cone while held; cone fits head and detaches on release; no conspicuous penetration or prop teleport at normal speed or key-frame review. | Close views of pickup, wearing, removal, release. |
| AC05 | Cone visibly contacts ground, rocks with decreasing amplitude and settles outside riding corridor. | S05–S06 capture and final placement. |
| AC06 | Freeze, guilty reaction, slow removal, sudden sprint and mounting fumble are distinct readable beats. | Normal-speed acting review of S03–S07. |
| AC07 | Hand/handlebar contact holds after the intended grip; feet contact the deck after their intended plants and through takeoff. The deliberate mounting fumble remains allowed; no visible pose jump occurs at handoff. | Side view plus chase capture spanning S07–S08. |
| AC08 | Camera establishes scooter, reveals officer, preserves direction and avoids scenery clipping or unintended handoff cuts/snaps. | Full capture in every supported environment. |
| AC09 | Required cues are audible without clipping; impact and beep start within 100 ms of visual events; footsteps stop during freeze. | Capture with audio and cue/event timing log. |
| AC10 | Skip and completion produce equivalent clean gameplay state exactly once; intro time cannot advance scoring, hazards or damage. Officer remains visible independently of the second-hit timer under the proposed contract. | Deterministic state tests at every shot boundary and chase capture after handoff/clean escape interval. |
| AC11 | Start, held Start, skip, pause/resume, focus loss and restart follow contract without stale input, duplicate actors or orphan sounds. | State/cue tests and interactive checks. |
| AC12 | Shared assets are referenced rather than copied; identity/scale match gameplay; references resolve from a clean checkout/build. | Asset validation, clean build and visual comparison. |
| AC13 | Stage works in street mode and both Hannover maps, without actors in buildings or obstacles. | One full capture per environment and stage notes. |
| AC14 | Specification, runtime files, sound licence records and reproducible checks accompany a criterion-by-criterion review. | Delivery review. |

Review visual defects at the normal game viewport and in targeted close views.
Record accepted limitations explicitly; do not silently waive a criterion.
When implementing, add a review table here: AC ID, pass/fail, evidence path,
command/review method, reviewer/date and limitations. Do not mark passes ahead
of implementation. Captures belong in the ignored review-media area; link their
paths and describe results in the review record.

## Ownership and technical findings

`animation.md` owns requirements; `storyboard.svg` illustrates shot IDs.
Scene-specific runtime data and exports belong beside these files. Reference
shared models/clips in `Assets/Models/` instead of copying them. Editable sources
and provenance belong in `Art/assets/cone_hat/`; Python tooling stays ignored.

Inspected on 2026-11-02:
- Renderer uses exported OBJ poses; street mode samples four officer run poses.
  No established skeletal playback path exists for this scene.
- Rider sources include `rider_rig.blend` and `final_assembly.blend`; rig
  suitability still requires inspection.
- No audio playback implementation was found in Engine or RunnerGame C# code.
- Current gameplay phases: Ready, Running, Paused, Caught. Intro timing,
  input handling, sound cues and gameplay handoff still require implementation.

Choose animation authoring/export after rig inspection and compare playback
costs with the existing renderer. A timeline alone does not supply new motion.

## Decisions to confirm before implementation

- 12-second baseline and storyboard staging.
- Playback, replay, skip and pause defaults.
- Continuous officer visibility after handoff, separate from timed damage pursuit.
- Three-environment delivery scope.
- Animation authoring/export after rig inspection; sound sources before final production.

These are tracked decisions, not permission to omit actions or acceptance evidence.
