# Cone launch audio - flight revision 2

Original project-authored cartoon foley, created/revised 2026-11-07, CC0-1.0.
No external recordings, speech or third-party sound samples. Runtime mix is
17 seconds, mono 44.1 kHz PCM16. Peak -8.69 dBFS, zero clipped samples.

## Current flight direction

Replaces the previous swept-sine spring chirps and amplitude-pulsed white noise.
Two seeded noise filters form a smooth air band, with changing upper cutoff,
soft attack/release and a shaped launch envelope. The rider launch is a short
1.25-second air sweep from 1.1 s; officer takeoff is a quieter 0.8-second sweep
from 4.1 s. A very quiet air bed supports flight, ducks around the 7.3-second
paper slap and fades with distance. The officer fall uses a short soft air cue;
departure fades as the camera pulls away. No repeated chirp or regular flutter.

Impacts, run steps, scooter landing, paper slap and final twinkle are preserved
as exact original non-flight stems. The ignored revision script reconstructs the
original random stream and verifies that its pre-revision WAV matches the old
installed mix byte-for-byte before replacing only the flight components.

Production: local ignored Art/assets/cone_crash/audio.py is the legacy source;
revise_flight_audio.py builds three auditions and the selected soft-air revision.
It writes scratch audition outputs under tools/asset-spike/out/cone-audio-review.
The selected delivery is crash.wav; event times are in audio-cues.json and
technical evidence is in audio-validation.json. Do not rerun the legacy script
alone to regenerate the current mix. Current sound still requires user listening
review; previously accepted motion remains unchanged.
