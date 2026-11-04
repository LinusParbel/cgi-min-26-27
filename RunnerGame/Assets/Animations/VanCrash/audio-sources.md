# Van crash audio sources

`crash.wav` is original deterministic synthesized cartoon foley authored for this
project on 2026-11-03, extended for the officer-ticket gag on 2026-11-04. No recordings, music, speech, downloaded samples or external
audio libraries are incorporated. New sound material is dedicated to CC0-1.0.

Authoring method: seeded noise bursts, exponentially decaying sine partials for
metal and impacts, a descending chirp for the fall, and short squeaks/ticks.
The ignored local `Art/assets/van_crash/audio.py` is the generation tool.
Mono PCM, 44,100 Hz, signed 16-bit, exactly eleven seconds. Only peak attenuation
is applied; no pitch-shifted voice or imitation of a real performer.

| Scene time | Cue | Processing |
|---|---|---|
| 0.00 | Hollow metal impact | Decaying 121/387/811 Hz partials and low noise |
| 0.48–2.16 | Cracks and collapse | Short seeded-noise transients and debris tail |
| 3.02 | Questioning squeak | Brief upward chirp, quiet |
| 3.30–4.35 | Fall | Descending sine chirp with smooth envelope |
| 3.31–3.72 | Scooter rattle | Three short metallic decays at the shared fall onset |
| 4.45 | Distant thump | Quiet low partial and noise tail |
| 2.70–5.11 | Officer run footfalls | Distance/half-stride cue times, damped noise and low partial, increasing level on approach |
| 5.26 | Braking scuff | Short noise envelope during deceleration |
| 6.65 | Jacket/ticket handling | Soft shaped noise |
| 7.70–9.26 | Release and paper flutter | Repeated soft irregular rustles |
| 9.75 | Distant paper tap | Small decaying noise transient |

See [audio-validation.json](audio-validation.json) for hash, cue times and measured
peak: -1.724 dBFS, zero clipped PCM samples. The scene mix plays on a private
Windows waveOut device, pauses/resumes with scene state, seeks on drift greater
than 75 ms, stops on reset/completion and honors `--mute`. Non-Windows or unavailable
audio devices leave animation playable without sound. Native transport behavior
is checked separately from the final subjective sound/pacing review.

Feedback revision: the late stone cube and its 5.70 s tick were removed. Scooter
rattle now begins with the shared rider/scooter fall, rather than a delayed drop.
